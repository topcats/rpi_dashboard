<?php require_once('app_shared.php'); ?>
<?php
/**
 * rpi_dashboard
 * PHP Script to extract OneNote page content for use in eDataMenu
 * Will grab a menu recipe URL, extract the OneNote page content with images, and save as HTML
 *
 * Called from CLI with 3 Args:
 * 1. Site ID (to lookup calendar details)
 * 2. Recipe ID (to identify the recipe in saved data)
 * 3. Base64 Encoded URL of the OneNote page to extract
*/


/**
 * Build JSON lookup for weburl
 * Will Strip out any extra onenote: data
 * @param string $weburl OneNote page URL
 * @return string json post data
 */
function BuildJsonGetNotebook($weburl)
{
    // Check for back url
    $hasonenote = strpos($weburl, 'onenote:');
    if ($hasonenote !== false) {
        // Convert onenote: to https:
        $weburl = rtrim(substr($weburl, 0, $hasonenote));
    }

    $outjson = '{';
    $outjson .= '"webUrl":' . json_encode($weburl);
    $outjson .= '}';

    return $outjson;
}


/**
 * Obtain Section ID from weburl
 * @param string $weburl OneNote page URL
 * @return string ID string
 */
function GetSectionIDfromURL($weburl)
{   
    $targetstart = strpos($weburl, '&wdsectionfileid={');
    if ($targetstart !== false) {
        $weburl = substr($weburl, $targetstart + 18);
        $targetend = strpos($weburl, '}');
        if ($targetend !== false) {
            $weburl = substr($weburl, 0, $targetend);
        }
    }
    return $weburl;
}


/**
 * Obtain Page ID from weburl
 * @param string $weburl OneNote page URL
 * @return string ID string
 */
function GetPageIDfromURL($weburl)
{   
    $targetstart = strpos($weburl, '&wdpartid={');
    if ($targetstart !== false) {
        $weburl = substr($weburl, $targetstart + 11);
        $targetend = strpos($weburl, '}');
        if ($targetend !== false) {
            $weburl = substr($weburl, 0, $targetend);
        }
    }
    return $weburl;
}


/**
 * Reformat HTML content
 * @param string $inhtml Input HTML
 * @return string Reformatted HTML
 */
function ReformatHtml($inhtml)
{
    $outhtml = $inhtml;

    // Strip Body attributes
    if (strpos($outhtml, '<body') !== false) {
        $bodystart = strpos($outhtml, '<body');
        $bodyend = strpos($outhtml, '>', $bodystart);
        if ($bodyend !== false) {
            $bodyend += 1; // Include ending >
            $outhtml = str_replace(substr($outhtml, $bodystart, $bodyend - $bodystart), '<body>', $outhtml);
        }
    }

    // Strip H2 attributes
    while (strpos($outhtml, '<h2 ') !== false) {
        $h2start = strpos($outhtml, '<h2 ');
        $h2end = strpos($outhtml, '>', $h2start);
        if ($h2end !== false) {
            $h2end += 1; // Include ending >
            $outhtml = str_replace(substr($outhtml, $h2start, $h2end - $h2start), '<h2>', $outhtml);
        } else {
            break;
        }
    }

    // Remove any div position attr
    // <div style="position:absolute;left:16px;top:82px;width:548px">
    while (strpos($outhtml, '<div style="position:absolute;') !== false) {
        $stylestart = strpos($outhtml, '<div style="position:absolute;')+4;
        $styleend = strpos($outhtml, '"', $stylestart+10);
        if ($styleend !== false) {
            $styleend += 1; // Include ending "
            $styledatagone = substr($outhtml, $stylestart, $styleend - $stylestart);
            $outhtml = str_replace($styledatagone, '', $outhtml);
        } else {
            break;
        }
    }

    // Fix line breaks
    $haslinebreak = strpos($outhtml, chr(239).chr(191).chr(188));
    if ($haslinebreak !== false) {
        $outhtml = str_replace(chr(239).chr(191).chr(188), '<br />', $outhtml);
    }

    // Return fixed HTML
    return $outhtml;
}



// ########################################################
// MAIN APP

// 0. Load Args
$siteid = null;
$recipeid = null;
$recipeurl = null;
try {
    $siteid = $argv[1];
    $recipeid = $argv[2];
    $recipeurl = base64_decode($argv[3]);
} catch (Exception $e) {
    die("Invalid Arguments!\n". $e);
}
if ($siteid == null || $recipeid == null || $recipeurl == null) {
    die("Argument data not Found!\n");
}

// 1. Load Config
$jsonsite = json_decode(file_get_contents(file_siteconfig), true);
LoadConfig();

// 2. Check Token
// Die if not found or valid, but must refresh before use
if ($jsontoken == null || !isset($jsontoken->auth) || !isset($jsontoken->token) || !isset($jsontoken->token->access_token) || $jsontoken->token->access_token == '') {
    die("No Authentication Token!\n");
} else {
    // Use Refresh token
    if (!DoAuthenticationRefresh()) {
        die("No Authentication Token!\n");
    }
}

// 3 Get Site Data
LoadSiteData($siteid);
if ($sitedata == null || !isset($sitedata["menu"])) {
    die("Site Config Menu not Found!\n");
}


// 4. Get recipe Data

// 4.0 Clear any existing data for this recipe
$menudataroot = scandir(file_o365menudata);
foreach($menudataroot as $value) {
    if($value === '.' || $value === '..') {continue;}
    if(is_file(file_o365menudata."/".$value)) {
        if (str_starts_with($value, 'recipe_'.$siteid.'_'.$recipeid.'_') ) {
            // This is an existing file for this recipe, so delete it
            unlink(file_o365menudata."/".$value);
        }
        continue;
    }
}

// 4.1 Find Base URL
$jsonGetNotebook = BuildJsonGetNotebook($recipeurl);
$post_response = DoPost($jsontoken->token->access_token, o365_getnotebookfromweburl, $jsonGetNotebook);

if ($post_response == null) {
    die("No Response from GetNotebookFromWebUrl!\n");
} elseif (strpos($post_response, 'error') !== false) {
    die("Error Response from GetNotebookFromWebUrl!\n". $post_response);
}
$post_response_json = json_decode($post_response, true);

// 4.2 Get Page Content
$urlPageContent = BuildGetUrlNotebookPage($post_response_json['sectionsUrl'], GetSectionIDfromURL($recipeurl), GetPageIDfromURL($recipeurl));
$get_response = DoLookup($jsontoken->token->access_token, $urlPageContent);

// 4.3 Process any images
while (strpos($get_response, '<img ') !== false) {
    // Grab each img tag
    $imgstart = strpos($get_response, '<img ');
    $imgend = strpos($get_response, '>', $imgstart);
    $imgdata = substr($get_response, $imgstart, $imgend - ($imgstart-1));

    // Mark done
    $imgdatanew = str_replace('<img ', '<imgdone ', $imgdata);
    // Remove data-fullres-src attribute
    if (strpos($imgdatanew, 'data-fullres-src="') !== false) {
        $attrstart = strpos($imgdatanew, 'data-fullres-src="');
        $attrend = strpos($imgdatanew, '"', $attrstart+19);
        $attrdata = substr($imgdatanew, $attrstart, $attrend - ($attrstart-1));
        $imgdatanew = str_replace($attrdata, '', $imgdatanew);
    }
    // Remove data-fullres-src-type attribute
    if (strpos($imgdatanew, 'data-fullres-src-type="') !== false) {
        $attrstart = strpos($imgdatanew, 'data-fullres-src-type="');
        $attrend = strpos($imgdatanew, '"', $attrstart+23);
        $attrdata = substr($imgdatanew, $attrstart, $attrend - ($attrstart-1));
        $imgdatanew = str_replace($attrdata, '', $imgdatanew);
    }

    // Fix any double spaces
    $imgdatanew = str_replace('  ', ' ', $imgdatanew);
    $imgdatanew = str_replace('  ', ' ', $imgdatanew);

    // Get Mime Type
    $mimetype = '';
    if (strpos($imgdatanew, 'data-src-type="') !== false) {
        $attrstart = strpos($imgdatanew, 'data-src-type="')+15;
        $attrend = strpos($imgdatanew, '"', $attrstart);
        $mimetype = substr($imgdatanew, $attrstart, $attrend - $attrstart);
    }

    // Get Image URL
    $imgurl = '';
    if (strpos($imgdatanew, 'src="') !== false) {
        $attrstart = strpos($imgdatanew, 'src="')+5;
        $attrend = strpos($imgdatanew, '"', $attrstart);
        $imgurl = substr($imgdatanew, $attrstart, $attrend - $attrstart);
    }

    // Update Img tag
    $get_response = str_replace($imgdata, $imgdatanew, $get_response);

    // Get Image Data
    $imgurldownload = $imgurl;
    $imgurldownload = str_replace('/siteCollections/', '/sites/', $imgurldownload);
    $imgurldownload = str_replace('/$value', '/content', $imgurldownload);
    $imagedata = DoLookup($jsontoken->token->access_token, $imgurldownload);
    if ($imagedata != null) {
        $imagehash = md5($imagedata);
        $imageext = '';
        switch ($mimetype) {
            case 'image/png':
                $imageext = '.png';
                break;
            case 'image/jpeg':
                $imageext = '.jpg';
                break;
            case 'image/gif':
                $imageext = '.gif';
                break;
            default:
                $imageext = '';
                break;
        }
        $imagename = 'recipe_'.$siteid.'_'.$recipeid.'_'.$imagehash.$imageext;
        file_put_contents(file_o365menudata.$imagename, $imagedata);

        // Replace in HTML
        $get_response = str_replace('src="'.$imgurl.'"', 'src="'.$imagename.'"', $get_response);
    }
}
$get_response = str_replace('<imgdone ', '<img ', $get_response);

// 4.4 Format HTML
$get_response = ReformatHtml($get_response);

// 4.5 Save HTML
file_put_contents(file_o365menudata.'recipe_'.$siteid.'_'.$recipeid.'.html', $get_response);

?>

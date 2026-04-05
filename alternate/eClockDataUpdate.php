<?php require_once('app_shared.php'); ?>
<?php
/**
 * rpi_dashboard
 * =================
 * PHP Script to Add/Update Calendar Event in O365
 * Will grab calendar event data, check if it exists in O365, and update or create as needed
 * 
 * Called from CLI with 2 Args:
 * 1. Site ID (to lookup calendar details)
 * 2. Base64 Encoded JSON of Event Data
 */


function BuildEventJson($eventdata)
{
    # https://learn.microsoft.com/en-gb/graph/api/resources/event?view=graph-rest-1.0#json-representation
    $outjson = '{';
    $outjson .= '"createdDateTime":"' . format_TimefromEpoch($eventdata->Created) . '",';
    $outjson .= '"subject":' . json_encode($eventdata->Subject) . ',';
    $outjson .= '"location":{"displayName": ' . json_encode($eventdata->Location) . '},';
    $outjson .= '"start":{"dateTime":"' . format_TimefromEpoch($eventdata->Start) . '","timeZone":"UTC"},';
    $outjson .= '"end":{"dateTime":"' . format_TimefromEpoch($eventdata->End) . '","timeZone":"UTC"},';
    $outjson .= '"importance":"low",';
    $outjson .= '"showAs":"free",';
    $outjson .= '"sensitivity":"normal",';
    $outjson .= '"isReminderOn":"false",';
    $outjson .= '"body":{"contentType":"' . $eventdata->Body->contentType . '","content":' . json_encode($eventdata->Body->content) . '},';
    $outjson .= '"singleValueExtendedProperties":[{"id":"' . o365_calextendedid . '","value":"' . $eventdata->Id . '"}]';
    $outjson .= '}';

    return $outjson;
}



// ########################################################
// MAIN APP

// 0. Load Args
$siteid = null;
$updatedata = null;
try {
    $siteid = $argv[1];
    $updatedata = json_decode(base64_decode($argv[2]));
} catch (Exception $e) {
    die("Invalid Arguments!\n". $e);
}
if ($siteid == null || $updatedata == null) {
    die("Argument data not Found!\n");
}


// 1. Load Config
$jsonsite = json_decode(file_get_contents(file_siteconfig), true);
LoadConfig();
date_default_timezone_set('UTC');


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
if ($sitedata == null || !isset($sitedata["calendar"])) {
    die("Site Config Calendar not Found!\n");
}


// Check if calender item Already Exists
$search_url = BuildLookupUrlSearchEvent($sitedata["calendar"]["id"], $updatedata->Id);
$search_output_json = DoLookup($jsontoken->token->access_token, $search_url);
$search_output = json_decode($search_output_json, true);
if ($search_output != null) {
    if (!isset($search_output['value']) || count($search_output['value']) == 0) {
        // Double check
        // Lookup via subject and times
        $search_urlb = BuildLookupUrlSearchEventName($sitedata["calendar"]["id"], format_TimefromEpoch($updatedata->Start), format_TimefromEpoch($updatedata->End), $updatedata->Subject);
        $search_output_jsonb = DoLookup($jsontoken->token->access_token, $search_urlb);
        $search_outputb = json_decode($search_output_jsonb, true);
        if ($search_outputb != null && isset($search_outputb['value']) && count($search_outputb['value']) > 0) {
            $search_output = $search_outputb;
            echo("          FOUND");
        }
    }

    if (isset($search_output['value']) && count($search_output['value']) > 0) {
        // If found update??

        // 4.1 Grab existing Data
        $group_eventid = $search_output['value'][0]['id'];

        // 4.2 Produce Data
        $updatedatajson = BuildEventJson($updatedata);

        // 4.3 Build Patch URL
        $group_posturl = BuildPatchUrlCalendar($sitedata["calendar"]["id"], $group_eventid);
        
        // 5.1 Post Data
        $post_response = DoPatch($jsontoken->token->access_token, $group_posturl, $updatedatajson);

        // 5.2 Process Recurancy
        $post_response_json = json_decode($post_response, true);

        if ($post_response_json != null && isset($post_response_json['id'])) {
            echo("          UPDATED\n");
        } else {
            echo("          FAILED: UPDATE\n");
        }

    } else {
        // Add New

        // 4.1 Produce Data
        $updatedatajson = BuildEventJson($updatedata);

        // 4.2 Build Create URL
        $group_posturl = BuildPostUrlCalendar($sitedata["calendar"]["id"]);

        // 5.1 Post Data
        $post_response = DoPost($jsontoken->token->access_token, $group_posturl, $updatedatajson);

        // 5.2 Process Recurancy
        $post_response_json = json_decode($post_response, true);

        if ($post_response_json != null && isset($post_response_json['id'])) {
            echo("          CREATED\n");
        } else {
            echo("          FAILED: CREATE\n");
        }
    }
} else {
    echo("          FAILED: SEARCH\n");
}

?>

<?php
/**
 * rpi_dashboard
 * =================
 * PHP Script Shared library for access to O365
*/


# Global Config

const file_siteconfig = "conf/site.json";
const file_o365config = "conf/o365.json";
const file_o365token = "data/o365_token-php.json";
const file_o365caldata = "data/calendar/infopane_2s.json";
const file_o365menudata = "data/menu/";

const o365_scopes = "offline_access user.read Group.Read.All Notes.Read.All";
const o365_appurl = "https://login.microsoftonline.com/common/oauth2/nativeclient";
const o365_calextendedid = "String {8eccc264-6880-4ebe-992f-8888d2eeaa1d} Name webical";
const o365_groupcalendarurl = "https://graph.microsoft.com/v1.0/groups/{group-id}/calendar/";
const o365_getnotebookfromweburl = "https://graph.microsoft.com/v1.0/me/onenote/notebooks/GetNotebookFromWebUrl";



/**
 * Produces a URL for a user to use to obtain the auth code
 * @return string Full URL
 */
function GetAuthenticationURL()
{
    global $jsonconfig;
    global $jsontoken;

    $oURL = "https://login.microsoftonline.com/" . $jsonconfig->tenant_id . "/oauth2/v2.0/authorize?";
    $oURL .= "client_id=" . $jsonconfig->client_id;
    $oURL .= "&response_type=code";
    $oURL .= "&redirect_uri=" . rawurlencode(o365_appurl);
    $oURL .= "&response_mode=query";
    $oURL .= "&scope=" . rawurlencode(o365_scopes);
    $oURL .= "&state=12345";
    return $oURL;
}


/**
 * Process the Auth code and grab the token
 * @return bool True if all good
 */
function DoAuthenticationToken()
{
    global $jsonconfig;
    global $jsontoken;

    try {
        // build post
        $post_auth = 'client_id=' . $jsonconfig->client_id;
        $post_auth .= '&scope=' . rawurlencode(o365_scopes);
        $post_auth .= '&code=' . rawurlencode($jsontoken->auth->code);
        $post_auth .= '&redirect_uri=' . rawurlencode(o365_appurl);
        $post_auth .= '&grant_type=authorization_code';
        $post_auth .= '&client_secret=' . rawurlencode($jsonconfig->client_secret);

        $ch_auth = curl_init();
        curl_setopt($ch_auth, CURLOPT_URL, "https://login.microsoftonline.com/" . $jsonconfig->tenant_id . "/oauth2/v2.0/token");
        curl_setopt($ch_auth, CURLOPT_POST, 1);
        curl_setopt($ch_auth, CURLOPT_HTTPHEADER, array('Content-type: application/x-www-form-urlencoded'));
        curl_setopt($ch_auth, CURLOPT_POSTFIELDS, $post_auth);

        // receive server response ...
        curl_setopt($ch_auth, CURLOPT_HEADER, 0);
        curl_setopt($ch_auth, CURLOPT_RETURNTRANSFER, true);
        $ch_output = curl_exec($ch_auth);
        curl_close($ch_auth);

        if (!str_contains($ch_output, "access_token")) {
            throw new Exception("access_token not returned");
        }

        // Update Token & Save
        $jsontoken->token = null;
        $temptoken = json_encode($jsontoken);
        $temptoken = str_replace("null", $ch_output, $temptoken);

        file_put_contents(file_o365token, $temptoken);
        $jsontoken = json_decode($temptoken);

        return true;
    } catch (Exception $e) {
        echo "DoAuthenticationToken Failure: " . $e;
        return false;
    }
}


/**
 * Process the Refresh token and update the token
 * @return bool True if all good
 */
function DoAuthenticationRefresh()
{
    global $jsonconfig;
    global $jsontoken;

    try {
        // build post
        $post_auth = 'client_id=' . $jsonconfig->client_id;
        $post_auth .= '&scope=' . rawurlencode(o365_scopes);
        $post_auth .= '&refresh_token=' . rawurlencode($jsontoken->token->refresh_token);
        $post_auth .= '&grant_type=refresh_token';
        $post_auth .= '&client_secret=' . rawurlencode($jsonconfig->client_secret);

        $ch_auth = curl_init();
        curl_setopt($ch_auth, CURLOPT_URL, "https://login.microsoftonline.com/" . $jsonconfig->tenant_id . "/oauth2/v2.0/token");
        curl_setopt($ch_auth, CURLOPT_POST, 1);
        curl_setopt($ch_auth, CURLOPT_HTTPHEADER, array('Content-type: application/x-www-form-urlencoded'));
        curl_setopt($ch_auth, CURLOPT_POSTFIELDS, $post_auth);

        // receive server response ...
        curl_setopt($ch_auth, CURLOPT_HEADER, 0);
        curl_setopt($ch_auth, CURLOPT_RETURNTRANSFER, true);
        $ch_output = curl_exec($ch_auth);
        curl_close($ch_auth);

        if (!str_contains($ch_output, "access_token")) {
            throw new Exception("access_token not returned");
        }

        // Update Token & Save
        $jsontoken->token = null;
        $temptoken = json_encode($jsontoken);
        $temptoken = str_replace("null", $ch_output, $temptoken);

        file_put_contents(file_o365token, $temptoken);
        $jsontoken = json_decode($temptoken);

        return true;
    } catch (Exception $e) {
        echo "DoAuthenticationRefresh Failure: " . $e;
        return false;
    }
}


/**
 * Do the main data lookup
 * @param string $authtoken Authorization Token
 * @param string $url Request URL
 * @return string page data
 */
function DoLookup($authtoken, $url)
{
    $ch_headers = array(
        'Cache-Control: no-cache',
        'Authorization: Bearer ' . $authtoken
    );
    $ch_group = curl_init();
    curl_setopt($ch_group, CURLOPT_URL, $url);
    curl_setopt($ch_group, CURLOPT_HTTPHEADER, $ch_headers);
    // receive server response ...
    curl_setopt($ch_group, CURLOPT_HEADER, 0);
    curl_setopt($ch_group, CURLOPT_RETURNTRANSFER, true);
    $ch_output = curl_exec($ch_group);
    curl_close($ch_group);

    return $ch_output;
}


/**
 * Do the main data post
 * @link https://learn.microsoft.com/en-gb/graph/api/user-post-events?view=graph-rest-1.0&tabs=http
 * @param string $authtoken Authorization Token
 * @param string $url Target URL
 * @param string $postdata PostData
 * @return string JSON response
 */
function DoPost($authtoken, $url, $postdata)
{
    $ch_headers = array(
        'Cache-Control: no-cache',
        'Content-type: application/json',
        'Authorization: Bearer ' . $authtoken
    );
    $ch_group = curl_init();
    curl_setopt($ch_group, CURLOPT_URL, $url);
    curl_setopt($ch_group, CURLOPT_POST, 1);
    curl_setopt($ch_group, CURLOPT_HTTPHEADER, $ch_headers);
    curl_setopt($ch_group, CURLOPT_POSTFIELDS, $postdata);
    // receive server response ...
    curl_setopt($ch_group, CURLOPT_HEADER, 0);
    curl_setopt($ch_group, CURLOPT_RETURNTRANSFER, true);
    $ch_output = curl_exec($ch_group);
    curl_close($ch_group);

    return $ch_output;
}


/**
 * Do the main data post
 * @link https://learn.microsoft.com/en-gb/graph/api/event-update?view=graph-rest-1.0&tabs=http
 * @param string $authtoken Authorization Token
 * @param string $url Target URL
 * @param string $postdata PostData
 * @return string JSON response
 */
function DoPatch($authtoken, $url, $postdata)
{
    $ch_headers = array(
        'Cache-Control: no-cache',
        'Content-type: application/json',
        'Authorization: Bearer ' . $authtoken
    );
    $ch_group = curl_init();
    curl_setopt($ch_group, CURLOPT_URL, $url);
    curl_setopt($ch_group, CURLOPT_CUSTOMREQUEST, 'PATCH');
    curl_setopt($ch_group, CURLOPT_HTTPHEADER, $ch_headers);
    curl_setopt($ch_group, CURLOPT_POSTFIELDS, $postdata);
    // receive server response ...
    curl_setopt($ch_group, CURLOPT_HEADER, 0);
    curl_setopt($ch_group, CURLOPT_RETURNTRANSFER, true);
    $ch_output = curl_exec($ch_group);
    curl_close($ch_group);

    return $ch_output;
}

/**
 * Return a complete group calendar post URL
 * Used to create a new event
 * @link https://learn.microsoft.com/en-gb/graph/api/group-post-events?view=graph-rest-1.0&tabs=http#http-request
 * @param string $calendarid Calendar ID GUID
 * @return string Full URL
 */
function BuildPostUrlCalendar($calendarid)
{
    $geturl = o365_groupcalendarurl . 'events';
    $geturl = str_replace("{group-id}", $calendarid, $geturl);

    return $geturl;
}


/**
 * Return a complete group calendar patch URL
 * Used to update a event
 * @param string $calendarid Calendar ID GUID
 * @param string $eventid Event ID
 * @return string Full URL
 */
function BuildPatchUrlCalendar($calendarid, $eventid)
{
    $geturl = o365_groupcalendarurl . 'events/{event-id}';
    $geturl = str_replace("{group-id}", $calendarid, $geturl);
    $geturl = str_replace("{event-id}", $eventid, $geturl);

    return $geturl;
}


/**
 * Return a complete calendar event search URL
 * @link https://learn.microsoft.com/en-us/graph/api/singlevaluelegacyextendedproperty-get?view=graph-rest-1.0&tabs=http
 * @param string $calendarid Calendar ID GUID
 * @param string $eventwebcalid Web Cal ID
 * @return String Full URL
 */
function BuildLookupUrlSearchEvent($calendarid, $eventwebcalid)
{
    $o365_calextendedidencoded = str_replace(" ", "%20", o365_calextendedid);
    $geturl = o365_groupcalendarurl . 'events?$filter=singleValueExtendedProperties%2Fany(ep%3Aep%2FId%20eq%20\'' . $o365_calextendedidencoded . '\'%20and%20ep%2Fvalue%20eq%20\'{event-id}\')';
    $geturl = str_replace("{group-id}", $calendarid, $geturl);
    $geturl = str_replace("{event-id}", $eventwebcalid, $geturl);

    return $geturl;
}


/**
 * Return a complete calendar event search URL for a date time range and subject name
 * @link https://learn.microsoft.com/en-gb/graph/api/group-list-calendarview?view=graph-rest-1.0&tabs=http
 * @link https://learn.microsoft.com/en-us/graph/filter-query-parameter?tabs=http
 * @param string $calendarid Calendar ID GUID
 * @param string $eventdatefrom Event DateTime From string
 * @param string $eventdatetill Event DateTime Till string
 * @param string $eventsubject Event Subject
 * @return String Full URL
 */
function BuildLookupUrlSearchEventName($calendarid, $eventdatefrom, $eventdatetill, $eventsubject)
{
    // $eventsubjectencoded = str_replace(" ", "%20", $eventsubject);
    $eventdatefrom = str_replace("00.000Z", "00", $eventdatefrom);
    $eventdatetill = str_replace("00.000Z", "00", $eventdatetill);

    $geturl = o365_groupcalendarurl . 'calendarView?startDateTime={datefrom}&endDateTime={datetill}&$filter=subject%20eq%20\'{subject}\'';

    $geturl = str_replace("{group-id}", $calendarid, $geturl);
    $geturl = str_replace("{datefrom}", $eventdatefrom, $geturl);
    $geturl = str_replace("{datetill}", $eventdatetill, $geturl);
    $geturl = str_replace("{subject}", rawurlencode($eventsubject), $geturl);

    return $geturl;
}


/**
 * Return a complete primary group calendar lookup URL
 * @param string $calendarid Calendar ID GUID
 * @param int $dayspast Number of days into the past
 * @param int $daysfuture Number of days in the future
 * @return string Full URL
 */
function BuildLookupUrlCalendar($calendarid, $dayspast, $daysfuture)
{
    $geturl = o365_groupcalendarurl . 'calendarView?$top=240&startDateTime={datefrom}&endDateTime={datetill}&expand=attachments';
    $geturl = str_replace("{group-id}", $calendarid, $geturl);

    $dayspast = str_replace("-", "", $dayspast);
    $dtdays_past = new DateInterval('P' . $dayspast . 'D');
    $dtdatefrom = new DateTime();
    $dtdatefrom->sub($dtdays_past);
    $geturl = str_replace("{datefrom}", $dtdatefrom->format("Y-m-d"), $geturl);

    $dtdays_future = new DateInterval('P' . $daysfuture . 'D');
    $dtdatetill = new DateTime();
    $dtdatetill->add($dtdays_future);
    $geturl = str_replace("{datetill}", $dtdatetill->format("Y-m-d"), $geturl);

    return $geturl;
}


/**
 * Return a complete OneNote page content URL
 * @param string $sectionsurl Full notebook sections URL
 * @param string $sectionid notebook section ID
 * @param string $pageid notebook page ID
 * @return string Full URL
 */
function BuildGetUrlNotebookPage($sectionsurl, $sectionid, $pageid)
{
    // Process sectionsurl
    $targetstart = strpos($sectionsurl, 'notebooks/');
    if ($targetstart !== false) {
        $sectionsurl = substr($sectionsurl, 0, $targetstart);
    }
    $sectionsurl .= 'pages/';

    // Append page and section
    $sectionsurl .= '1-' . $pageid . '!1-' . $sectionid . '/content';

    return $sectionsurl;
}


/**
 * Load main O365 config and token files
 */
function LoadConfig()
{
    global $jsonconfig;
    global $jsontoken;

    // Load O365 Config
    $jsonconfig = json_decode(file_get_contents(file_o365config));

    // Load Token file
    if (file_exists(file_o365token)) {
        $jsontoken = json_decode(file_get_contents(file_o365token));
    } else {
        $jsontoken = null;
    }
}


/**
 * Load Site Data for a specific site
 * @param int $siteid Site ID
 */
function LoadSiteData($siteid)
{
    global $jsonsite;
    global $sitedata;

    $sitedata = null;

    // Loop round sites to find the right one
    foreach ($jsonsite["locations"] as $o) {
        if ($o['id'] == $siteid) {
            $sitedata = $o;
            break;
        }
    }

    // Check site was found
    if ($sitedata == null) {
        die("Site Config not Found!\n");
    }
}


function get_TimefromEpoch($in)
{
    if (is_numeric($in)) {
        $dt = new DateTime("@$in");
    } else {
        $dt = new DateTime($in);
    }
    return $dt;
}

function format_TimefromEpoch($in)
{
    $dt = get_TimefromEpoch($in);
    # if (date_default_timezone_get()) {
    #    $dt->setTimeZone(new DateTimeZone(date_default_timezone_get()));
    # }
    # 2025-07-02T21:56:18.906Z"
    return $dt->format('Y-m-d\TH:i:s.000\Z');
}

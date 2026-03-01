<?php
/**
 * rpi_dashboard
 * =================
 * PHP Script to Read Calendar Events from Shared Group Calendars in O365
 * 
 * Called from CLI:
 * Site ID is hardcoded to 2
*/


const file_siteconfig = "conf/site.json";
const file_o365config = "conf/o365.json";
const file_o365token = "data/o365_token-php.json";
const file_o365caldata = "data/calendar/infopane_2s.json";

const o365_scopes = "offline_access user.read Group.Read.All Notes.Read.All";
const o365_appurl = "https://login.microsoftonline.com/common/oauth2/nativeclient";

// Leverage the power of our client libraries. Download the PHP client library here https://aka.ms/graphphpsdk
// To read more about our SDKs, go to the documentation page at https://aka.ms/sdk-doc
// https://github.com/microsoftgraph/msgraph-sdk-php



/**
 * Produces a URL for a user to use to obtain the auth code
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
 * Return a complete primary group calendar lookup URL
 */
function BuildLookupUrlCalendar($calendarid, $dayspast, $daysfuture)
{
    $geturl = 'https://graph.microsoft.com/v1.0/groups/{group-id}/calendar/calendarView?$top=240&startDateTime={datefrom}&endDateTime={datetill}&expand=attachments';
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
 * Return a complete calendar event URL
 */
function BuildLookupUrlEvent($calendarid, $eventid)
{
    $geturl = 'https://graph.microsoft.com/v1.0/groups/{group-id}/calendar/events/{event-id}';
    $geturl = str_replace("{group-id}", $calendarid, $geturl);
    $geturl = str_replace("{event-id}", $eventid, $geturl);

    return $geturl;
}


/**
 * Do the main data lookup
 * Return page data as string
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
 * Simple Get Month Name
 */
function GetMonthName($value)
{
    return date('F', strtotime("2012-$value-01"));
}


/**
 * Produce Recurrence English Text
 */
function GetRecurrenceText($value)
{
    if (is_null($value) || is_null($value['recurrence'])) {
        return '';
    } else {
        // Base Values
        $value_index = (key_exists('index', $value['recurrence']['pattern']) && !is_null($value['recurrence']['pattern']['index'])) ? $value['recurrence']['pattern']['index'] : 'first';
        $value_interval = (key_exists('interval', $value['recurrence']['pattern']) && !is_null($value['recurrence']['pattern']['interval'])) ? $value['recurrence']['pattern']['interval'] : null;
        $value_month = (key_exists('month', $value['recurrence']['pattern']) && !is_null($value['recurrence']['pattern']['month']) && $value['recurrence']['pattern']['month'] != 0) ? $value['recurrence']['pattern']['month'] : null;
        $r_range = "";

        // Get Interval
        $pattern = sprintf(
            "Daily: every %sday%s",
            ($value_interval != 1) ? $value_interval . ' ' : '',
            ($value_interval != 1) ? 's' : ''
        );

        if (key_exists('daysOfWeek', $value['recurrence']['pattern']) && !is_null($value['recurrence']['pattern']['daysOfWeek'])) {
            $days = implode(' or ', $value['recurrence']['pattern']['daysOfWeek']);
            $pattern = sprintf(
                'Relative Monthly: %s %s every %smonth%s',
                $value_index,
                $days,
                ($value_interval != 1) ? $value_interval . ' ' : '',
                ($value_interval != 1) ? 's' : ''
            );
            if (key_exists('firstDayOfWeek', $value['recurrence']['pattern']) && !is_null($value['recurrence']['pattern']['firstDayOfWeek'])) {
                $pattern = sprintf(
                    'Weekly: every %sweek%s on %s',
                    ($value_interval != 1) ? $value_interval . ' ' : '',
                    ($value_interval != 1) ? 's' : '',
                    $days
                );
            } elseif (!is_null($value_month)) {
                $pattern = sprintf(
                    'Relative Yearly: %s %s every %syear%s on %s',
                    $value_index,
                    $days,
                    ($value_interval != 1) ? $value_interval . ' ' : '',
                    ($value_interval != 1) ? 's' : '',
                    GetMonthName($value_month)
                );
            }
        } elseif (key_exists('dayOfMonth', $value['recurrence']['pattern']) && !is_null($value['recurrence']['pattern']['dayOfMonth']) && $value['recurrence']['pattern']['dayOfMonth'] != 0) {
            $pattern = sprintf(
                'Absolute Monthly: on day %s every %smonth%s',
                $value['recurrence']['pattern']['dayOfMonth'],
                ($value_interval != 1) ? $value_interval . ' ' : '',
                ($value_interval != 1) ? 's' : ''
            );
            if (!is_null($value_month)) {
                $pattern = sprintf(
                    'Absolute Yearly: on %s %s every %syear%s',
                    GetMonthName($value_month),
                    $value['recurrence']['pattern']['dayOfMonth'],
                    ($value_interval != 1) ? $value_interval . ' ' : '',
                    ($value_interval != 1) ? 's' : ''
                );
            }
        }

        // Get Range
        if (key_exists('range', $value['recurrence']) && key_exists('startDate', $value['recurrence']['range']) && !is_null($value['recurrence']['range']['startDate'])) {
            $r_range = sprintf('Starting on %s', $value['recurrence']['range']['startDate']);
            $ends_on = 'with no end';
            if (key_exists('endDate', $value['recurrence']['range']) && !is_null($value['recurrence']['range']['endDate']) && $value['recurrence']['range']['endDate'] != '0001-01-01') {
                $ends_on = sprintf('ending on %s', $value['recurrence']['range']['endDate']);
            } elseif (key_exists('numberOfOccurrences', $value['recurrence']['range']) && !is_null($value['recurrence']['range']['numberOfOccurrences']) && $value['recurrence']['range']['numberOfOccurrences'] >= 1) {
                $ends_on = sprintf(
                    'up to %s occurrence%s',
                    $value['recurrence']['range']['numberOfOccurrences'],
                    ($value['recurrence']['range']['numberOfOccurrences'] != 1) ? 's' : ''
                );
            }
            $r_range = sprintf('%s %s', $r_range, $ends_on);
        }
        return sprintf("%s. %s", $pattern, $r_range);
    }
}


// ########################################################
// MAIN APP

// 0. Load Config
$jsonsite = json_decode(file_get_contents(file_siteconfig), true);
$jsonconfig = json_decode(file_get_contents(file_o365config));

if (file_exists(file_o365token)) {
    $jsontoken = json_decode(file_get_contents(file_o365token));
} else {
    $jsontoken = null;
}


// 1. Check if have a token (does not check valid), else die
if ($jsontoken == null || !isset($jsontoken->auth)  || !isset($jsontoken->auth->code) || $jsontoken->auth->code == '') {
    echo "Authentication URL:\n\n" . GetAuthenticationURL() . "\n\n";
    die("No Authentication!\n");
}


// 2. Get Access Token
if ($jsontoken == null || !isset($jsontoken->token) || !isset($jsontoken->token->access_token) || $jsontoken->token->access_token == '') {
    // Do normal access token aquire
    if (!DoAuthenticationToken()) {
        die("No Authentication Token!\n");
    }
} else {
    // Use Refresh token
    if (!DoAuthenticationRefresh()) {
        die("No Authentication Token!\n");
    }
}


// 3 Get Data
// https://learn.microsoft.com/en-us/graph/auth-v2-user?context=graph%2Fapi%2F1.0&view=graph-rest-1.0&tabs=curl

// 3.1 Get Site Data
$siteid = "2";
$sitedata = null;
foreach ($jsonsite["locations"] as $o) {
    if ($o['id'] == $siteid) {
        $sitedata = $o;
        break;
    }
}

if ($sitedata == null || !isset($sitedata["calendar"])) {
    die("Site Config not Found!\n");
}

// 3.2 Build URL
$group_geturl = BuildLookupUrlCalendar($sitedata["calendar"]["id"], $sitedata["calendar"]["days_past"], $sitedata["calendar"]["days_future"]);

// 3.3 Get Data
$ch_output = DoLookup($jsontoken->token->access_token, $group_geturl);

// 3.5 Process Recurancy
$json_output = json_decode($ch_output, true);

foreach ($json_output["value"] as &$o) {
    if ($o['seriesMasterId'] != null) {
        $event_geturl = BuildLookupUrlEvent($sitedata["calendar"]["id"], $o['seriesMasterId']);

        $event_json = json_decode(DoLookup($jsontoken->token->access_token, $event_geturl), true);

        $o['recurrence'] = GetRecurrenceText($event_json);
    }
}


// 4 Save Data
$ch_output = json_encode($json_output);
file_put_contents(file_o365caldata, $ch_output);

?>

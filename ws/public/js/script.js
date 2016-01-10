// common variables
var iBytesUploaded = 0;
var iBytesTotal = 0;
var iPreviousBytesLoaded = 0;
var iMaxFilesize = 1048576; // 1MB
var oTimer = 0;
var sResultFileSize = '';
var resTimer = 0;

function secondsToTime(secs) { // we will use this function to convert seconds in normal time format
    var hr = Math.floor(secs / 3600);
    var min = Math.floor((secs - (hr * 3600))/60);
    var sec = Math.floor(secs - (hr * 3600) -  (min * 60));

    if (hr < 10) {hr = "0" + hr; }
    if (min < 10) {min = "0" + min;}
    if (sec < 10) {sec = "0" + sec;}
    if (hr) {hr = "00";}
    return hr + ':' + min + ':' + sec;
};

function bytesToSize(bytes) {
    var sizes = ['Bytes', 'KB', 'MB'];
    if (bytes == 0) return 'n/a';
    var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
    return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + sizes[i];
};

function fileSelected() {

    // hide different warnings
    document.getElementById('upload_response').style.display = 'none';
    document.getElementById('error').style.display = 'none';
    document.getElementById('error2').style.display = 'none';
    document.getElementById('abort').style.display = 'none';
    document.getElementById('warnsize').style.display = 'none';

    document.getElementById('upload_btn').disabled = false;
    document.getElementById('execute_btn').disabled = true;
    document.getElementById('optimize_btn').disabled = true;
    document.getElementById('ref_perf').innerHTML = '';

    // get selected file element
    var oFile = document.getElementById('prog_file').files[0];

    // filter for Fortran source files
    //var rFilter = /^(image\/bmp|image\/gif|image\/jpeg|image\/png|image\/tiff)$/i;
    var rFilter = /^(text\/x\-fortran|text\/x\-csrc|text\/x\-c\+\+src|application\/octet\-stream)$/i;
    if (! rFilter.test(oFile.type)) {
        document.getElementById('error').style.display = 'block';
        return;
    }

    // little test for filesize
    if (oFile.size > iMaxFilesize) {
        document.getElementById('warnsize').style.display = 'block';
        return;
    }
}

function startUploading() {
    // cleanup all temp states
    iPreviousBytesLoaded = 0;
    document.getElementById('upload_response').style.display = 'none';
    document.getElementById('error').style.display = 'none';
    document.getElementById('error2').style.display = 'none';
    document.getElementById('abort').style.display = 'none';
    document.getElementById('warnsize').style.display = 'none';
    document.getElementById('progress_percent').innerHTML = '';
    document.getElementById('ref_perf').innerHTML = '';
    //var oProgress = document.getElementById('progress');
    //oProgress.style.display = 'block';
    //oProgress.style.width = '0px';

    // get form data for POSTing
    //var vFD = document.getElementById('upload_form').getFormData(); // for FF3
    var vFD = new FormData(document.getElementById('upload_form')); 

    // create XMLHttpRequest object, adding few event listeners, and POSTing our data
    var oXHR = new XMLHttpRequest();        
    //oXHR.upload.addEventListener('progress', uploadProgress, false);
    oXHR.addEventListener('load', uploadFinish, false);
    oXHR.addEventListener('error', uploadError, false);
    oXHR.addEventListener('abort', uploadAbort, false);
    oXHR.open('POST', 'upload');
    oXHR.send(vFD);

	if ( resTimer != 0 ) clearInterval(resTimer);
	document.getElementById('ref_perf_wait').innerHTML = '';

    // set inner timer
    //oTimer = setInterval(doInnerUpdates, 300);
}

function executeProgram() {
    var oXHR = new XMLHttpRequest();
	var params = 'build='+document.getElementById('compile_cmd').value;
    oXHR.addEventListener('load', executeFinish, false);
    oXHR.open('GET', 'execute?'+encodeURI(params), true);
	oXHR.setRequestHeader("Content-type", "text/plain");
    oXHR.send();
    resTimer = setInterval(waitRefResponse, 5000);
}

function waitRefResponse() {
    var oXHR = new XMLHttpRequest();
	var params = 'getinfo=ref_result'
    oXHR.open('GET', 'execute?'+encodeURI(params), false);
	oXHR.setRequestHeader("Content-type", "text/plain");
    oXHR.send();
	document.getElementById('ref_perf').innerHTML = oXHR.responseText;

	if (oXHR.responseText.length>8 && oXHR.responseText.substring(0,9)=='COMPLETED') {
		clearInterval(resTimer);
		document.getElementById('optimize_btn').disabled = false;
	} else {
		var dots = document.getElementById('ref_perf_wait').innerHTML;
		if ( dots.length>50 ) dots = '';
		document.getElementById('ref_perf_wait').innerHTML = dots + '.';
	}
}

function executeFinish(evt) {
}

function optimizeProgram() {
}

function doInnerUpdates() { // we will use this function to display upload speed
    var iCB = iBytesUploaded;
    var iDiff = iCB - iPreviousBytesLoaded;

    // if nothing new loaded - exit
    if (iDiff == 0)
        return;

    iPreviousBytesLoaded = iCB;
    iDiff = iDiff * 2;
    var iBytesRem = iBytesTotal - iPreviousBytesLoaded;
    var secondsRemaining = iBytesRem / iDiff;

    // update speed info
    var iSpeed = iDiff.toString() + 'B/s';
    if (iDiff > 1024 * 1024) {
        iSpeed = (Math.round(iDiff * 100/(1024*1024))/100).toString() + 'MB/s';
    } else if (iDiff > 1024) {
        iSpeed =  (Math.round(iDiff * 100/1024)/100).toString() + 'KB/s';
    }

    document.getElementById('speed').innerHTML = iSpeed;
    document.getElementById('remaining').innerHTML = '| ' + secondsToTime(secondsRemaining);        
}

function uploadProgress(e) { // upload process in progress
    if (e.lengthComputable) {
        iBytesUploaded = e.loaded;
        iBytesTotal = e.total;
        var iPercentComplete = Math.round(e.loaded * 100 / e.total);
        var iBytesTransfered = bytesToSize(iBytesUploaded);

        document.getElementById('progress_percent').innerHTML = iPercentComplete.toString() + '%';
        document.getElementById('progress').style.width = (iPercentComplete * 4).toString() + 'px';
        document.getElementById('b_transfered').innerHTML = iBytesTransfered;
        if (iPercentComplete == 100) {
            var oUploadResponse = document.getElementById('upload_response');
            oUploadResponse.innerHTML = '<h1>Please wait...processing</h1>';
            oUploadResponse.style.display = 'block';
        }
    } else {
        document.getElementById('progress').innerHTML = 'unable to compute';
    }
}

function uploadFinish(e) { // upload successfully finished
    var oUploadResponse = document.getElementById('upload_response');
    oUploadResponse.innerHTML = e.target.responseText;
    oUploadResponse.style.display = 'block';

    //document.getElementById('progress_percent').innerHTML = '100%';
    //document.getElementById('progress').style.width = '400px';
    //document.getElementById('filesize').innerHTML = sResultFileSize;
    //document.getElementById('remaining').innerHTML = '| 00:00:00';
    document.getElementById('compile_cmd').disabled = false;
    document.getElementById('execute_btn').disabled = false;

    clearInterval(oTimer);
}

function uploadError(e) { // upload error
    document.getElementById('error2').style.display = 'block';
    clearInterval(oTimer);
}  

function uploadAbort(e) { // upload abort
    document.getElementById('abort').style.display = 'block';
    clearInterval(oTimer);
}


<div class="popupform" id="newclub">
<h3>New Club</h3>
<form action="#" method="post" onsubmit="submitClub(this);return false;">
Name: <input type="text" name="name" required><br>
About: <textarea id="newclubabout"></textarea><br>
<ul id="memberTags"></ul>
<!-- All Friends: <input type="checkbox" ><br> -->
<ul id="adminTags"></ul>
            <div class="onoffswitch" id="publicswpar">
                <input type="checkbox" name="onoffswitch" class="onoffswitch-checkbox" id="publicsw" checked>
                <label class="onoffswitch-label" for="publicsw" >
                    <div class="onoffswitch-inner" titleb="Private" titlea="Public"></div>
                    <div class="onoffswitch-switch"></div>
                </label>
            </div>
<a href="#" onclick="$('#newclub').fadeOut()">Cancel</a>
<input type="submit" value="Create">

</form>
</div>
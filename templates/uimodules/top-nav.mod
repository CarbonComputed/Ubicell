{%from actions import *%}
    <div id="nav">

        <div id="left-nav">
            <div id="logo">
                <a href="/" class="fill-div"></a>
                <img src="/static/images/logo_word6.svg" href="/" height="55px" width="175px">
            </div>
        </div>
        <div id="center-nav">

            <div id="search-area">
                <form action="#" onsubmit="searchFriends();return false;">
                <input class="search_box" type="text" name="search" placeholder="Search..." >
                <!-- <a class="btn" href="#" onclick="searchFriends()"><i class="icon-search"></i></a> -->
                </form>
            </div>
        </div>
        <div id="right-nav">
            <div id="not">
            {%set nc = len(core_actions.get_unread_notifications(current_user['_id']['$oid']))%}
            {%if nc > 0%}
            <a href="#" onclick="toggleNotifications();return false;" style="text-decoration:none;"> <i style="color:orange;" class="icon-globe icon-large"><span class="notification-count">{{nc}}</span></i></a>
            
            {%else%}
                <a href="#" onclick="toggleNotifications();return false;" style="text-decoration:none;"> <i style="color:black;" class="icon-globe icon-large"><span style="display:none;" class="notification-count">{{nc}}</span></i></a>
            {%end%}

                {%from models.Notification import *%}
                <div id="not-menu-cont">
                <div id="not-menu">

                    {%for n in nots%}
                    {%module NotModule(n)%}
                    {%end%}


            </div>
            </div>
            </div>
            <span class="nav-bar">
                <a href="/">Feed</a>
                <a href="/user/{{escape(current_user['UserName'])}}">Profile</a>
                <!-- <a class = "btn" id="setting" href="#"><i class="icon-cogs"></i></a> -->
                <div id="dd" class="wrapper-dropdown-2" tabindex="1"><i id="tab" class="icon-cogs icon-small"></i>
                    <ul class="dropdown">
                        <!-- <li><a href="#"><i class="icon-envelope icon-small"></i>Make Event</a></li>
                        <li><a href="#"><i class="icon-envelope icon-small"></i>Make Group</a></li> -->
                        <li><a href="#"><i class="icon-upload"></i>Add Photos</a></li>
                        <li><a href="/actions/edit_profile"><i class="icon-edit icon-small"></i>Edit Profile</a></li>
                        <li><a href="/auth/logout"><i class="icon-signout icon-small"></i>Logout</a></li>
                    </ul>
                </div>
            </div>
        </span>
    </div>
    </div>
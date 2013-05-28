{%from actions import *%}
{%from models.Notification import *%}

<div class="not-item">
    {%if isinstance(n,FriendRequestNot)%}
    {%set friend = user_actions.get_simple_data(n.Friend)%}
    <a href="/user/{{friend.UserName}}" class="fill-div"><span></span></a>
    <img src="/images?picid={{str(friend.ProfileImg)}}" href="/user/{{friend.UserName}}" height="52" width="52">
    <p>{{n.Message}}</p>
    {%end%}
</div>
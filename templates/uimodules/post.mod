{%from actions import *%}

<div id="status-sec" data-postid={{post.id}} data-vote={{me.Votes.get(str(post.id),0)}}  >
<div id="votes">
{%set color = 'gray'%}
{% if me.Votes.get(str(post.id),0)  == 1 %}
    {%set color = 'orange'%}
{%end%}
    <a  class="upvote" href="#" onclick="vote(this,'up');return false;" ><i style="color:{{color}};" class="icon-arrow-up"></i></a>
    <p>{{post.Upvotes-post.Downvotes}}</p>
{%set color = 'gray'%}
    {% if me.Votes.get(str(post.id),0)  == -1 %}
        {%set color = 'blue'%}
    {%end%}
    <a class="downvote" href="#" onclick="vote(this,'down');return false;"><i style="color:{{color}};" class="icon-arrow-down"></i></a>
    <div class="clear"></div>

</div>
{%set user = user_actions.get_simple_data(post.UserId)%}
{%set friend = user_actions.get_simple_data(post.FriendId)%}
{%if detailed and post.NetworkId != post.UserId and post.FriendId == post.UserId %}
                        {%from models.Club import *%}
                        {%set network = Club.objects(id=post.NetworkId).first()%}
                        {%if network == None%}
                        {%set netname = uniname%}
                        {%set url = '/university'%}
                        {%else%}
                        {%set netname = network.Name%}
                        {%set url = '/club?clubid='+str(network.id)%}
                        {%end%}
                        {%from actions import *%}
                        {%set user = user_actions.get_simple_data(post.UserId)%}
                        {%set friend = user_actions.get_simple_data(post.FriendId)%}
                    <div id="status-post">

                                            <a href="/user/{{friend.UserName}}"><img src="/images?picid={{str(friend.ProfileImg)}}" href="/user/{{friend.UserName}}" height="52" width="52"></a>
                                            <div class="status-info">
                        <p><a class="name" href="/user/{{friend.UserName}}">{{friend.FirstName.capitalize()}} {{friend.LastName.capitalize()}}</a><i class="icon-caret-right" style="color:black;margin-top:5px;"></i><a class="name" href="{{url}}">{{netname}}</a></p>
                        <p class="post">{% raw linkify(post.Message)%}</p>
                        <a id="show-comment-link" href="#" onclick="toggleReplies(this);return false;"style="float:left;background:white;font-size:11px;padding-top:10px;color:black;">Show Comments</a>
                        <a href="#" onclick="displayReply(this);return false;" style="float:left;background:white;font-size:11px;padding-top:10px;color:black;padding-left:10px;">Reply</a>                     

                    </div>
                </div>
{%elif detailed and post.FriendId != post.UserId%}
                    <div id="status-post">

                                            <a href="/user/{{friend.UserName}}"><img src="/images?picid={{str(friend.ProfileImg)}}" href="/user/{{friend.UserName}}" height="52" width="52"></a>
                                            <div class="status-info">
                        <p><a class="name" href="/user/{{friend.UserName}}">{{friend.FirstName.capitalize()}} {{friend.LastName.capitalize()}}</a><i class="icon-caret-right" style="color:black;margin-top:5px;"></i><a class="name" href="/user/{{user.UserName}}">{{user.FirstName.capitalize()}} {{user.LastName.capitalize()}}</a></p>
                        <p class="post">{% raw linkify(post.Message)%}</p>
                        <a id="show-comment-link" href="#" onclick="toggleReplies(this);return false;"style="float:left;background:white;font-size:11px;padding-top:10px;color:black;">Show Comments</a>
                        <a href="#" onclick="displayReply(this);return false;" style="float:left;background:white;font-size:11px;padding-top:10px;color:black;padding-left:10px;">Reply</a>                     

                    </div>
                </div>
{%elif detailed and post.FriendId == post.UserId%}
                            <div id="status-post">
                                <a href="/user/{{user['UserName']}}"><img src="/images?picid={{str(user['ProfileImg'])}}" href="/user/{{user.UserName}}" height="52" width="52"></a>
                                <div class="status-info">
                                <a class="name" href="/user/{{user.UserName}}">{{user['FirstName'].capitalize()}} {{user['LastName'].capitalize()}}</a></br>
                                <p class="post">{% raw linkify(post['Message'])%}</p>
                                <a id="show-comment-link" href="#" onclick="toggleReplies(this);return false;" style="float:left;background:white;font-size:11px;padding-top:10px;color:black;">Show Comments</a>
                                <a href="#" onclick="displayReply(this);return false;"style="float:left;background:white;font-size:11px;padding-top:10px;color:black;padding-left:10px;">Reply</a>
                                <p></p>
                                </div>
                            </div>
{%elif not detailed and post.FriendId == post.UserId%}
                            <div id="status-post">
                                <a href="/user/{{user['UserName']}}"><img src="/images?picid={{str(user['ProfileImg'])}}" href="/user/{{user.UserName}}" height="52" width="52"></a>
                                <div class="status-info">
                                <a class="name" href="/user/{{user.UserName}}">{{user['FirstName'].capitalize()}} {{user['LastName'].capitalize()}}</a></br>
                                <p class="post">{% raw linkify(post['Message'])%}</p>
                                <a id="show-comment-link" href="#" onclick="toggleReplies(this);return false;" style="float:left;background:white;font-size:11px;padding-top:10px;color:black;">Show Comments</a>
                                <a href="#" onclick="displayReply(this);return false;"style="float:left;background:white;font-size:11px;padding-top:10px;color:black;padding-left:10px;">Reply</a>
                                <p></p>
                                </div>
                            </div>
{%elif not detailed and post.FriendId != post.UserId%}
                            <div id="status-post">
                                <a href="/user/{{friend['UserName']}}"><img src="/images?picid={{str(friend['ProfileImg'])}}" href="/user/{{friend.UserName}}" height="52" width="52"></a>
                                <div class="status-info">
                                <a class="name" href="/user/{{friend.UserName}}">{{friend['FirstName'].capitalize()}} {{friend['LastName'].capitalize()}}</a></br>
                                <p class="post">{% raw linkify(post['Message'])%}</p>
                                <a id="show-comment-link" href="#" onclick="toggleReplies(this);return false;" style="float:left;background:white;font-size:11px;padding-top:10px;color:black;">Show Comments</a>
                                <a href="#" onclick="displayReply(this);return false;"style="float:left;background:white;font-size:11px;padding-top:10px;color:black;padding-left:10px;">Reply</a>
                                <p></p>
                                </div>
                            </div>

{%else%}
<h2>helllooo</h2>
{%end%}

    <div class="clear"></div>
<div class="reply-box" data-postid={{post.id}}  style="text-align:left;"> 
        <form>
            <textarea class="reply_text_id" class="reply_text"></textarea>
            <div >
                <a class="rep_link" onclick="reply(this);return false;" href="#">Reply</a>
                <a onclick="hideReply(this);return false;" href="#">Cancel</a>
            </div>
        </form>
    </div>
    {%block reply_sec%}

    {%end%}
    <div class="reply-sec" style= "padding-top:15px;font-size:75%;background:white;">

    </div>
</div>
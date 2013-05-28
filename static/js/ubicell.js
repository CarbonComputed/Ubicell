PostType = {
    WALL_POST : 1,
    REPLY_POST : 2,
}

MemberAction = {
    ADD : 1,
    DELETE : 2,
    PROMOTE : 3,
    CONFIRM : 4
}

function loadReplies(ele){

    var ssec = $(ele).closest('#status-sec')
    var nele = ssec.find('.reply-sec');
    var postid = ssec.data()['postid'];
    var ownerid = ssec.data()['ownerid'];

    //var postid = 
    $(nele).load('/actions/get_replies?post_id='+postid).hide().fadeIn(300);
    $(ssec).find('#show-comment-link').html("Hide Comments");

}

function searchFriends(){
    var query = $('.search_box').val();
    $('head').append('<link rel="stylesheet" type="text/css" href="/static/styles/search.css">');
//  $('#Main-Content').load("/search?" + $.param({ query : query}) + " #Main-Content > *").hide().fadeIn(700);
    window.location = ("/search?" + $.param({ query : query}));
}

function vote(ele,type){
    var postid = $(ele).closest('#status-sec').data()['postid'];
    var vote = $(ele).closest('#status-sec').data('vote');
    var current_score_ele =  $(ele).closest('#status-sec').find('p').first();
    var score = parseInt(current_score_ele.text());
    //var ownerid = $(ele).closest('#status-sec').data()['ownerid'];
    $.ajax({
          type: "POST",
          url: '/actions/friend_vote',
          data: { 'vote_type' : type,'post_id' : postid,'is_reply' : false},
          success: function(){ 
              //console.log(ele);
              var current_page = document.URL;
              //console.log(vote);
              if(vote == -1){
                if(type == "up"){
                console.log($(ele).eq(0));
                 $(ele).closest('#status-sec').data('vote',0);
                 $(ele).eq(0).siblings('a.downvote').children().eq(0).css('color','gray');
                 current_score_ele.text(score+1);
                } 
              }
              else if(vote == 0){
                if(type == "up"){
                 $(ele).closest('#status-sec').data('vote',1);
                 $(ele).children().eq(0).css('color','orange');
                 current_score_ele.text(score+1);

                }
                if(type == "down"){
                 $(ele).closest('#status-sec').data('vote',-1);
                 //console.log($(ele).children().eq(0));
                 $(ele).children().eq(0).css('color','blue');
                 current_score_ele.text(score-1);
                }
              }
              else if(vote == 1){
                if(type == "down"){
                 $(ele).closest('#status-sec').data('vote',0);
                   //console.log($(ele).children().eq(0));
                   //console.log($(ele).eq(0).prevAll('a.upvote').first());
                   $(ele).eq(0).prevAll('a.upvote').first().children().eq(0).css('color','gray');
                   current_score_ele.text(score-1);


                }
              }
              

              //$("#status-sec[data-postid='" + postid + "']").load(current_page+" #status-sec[data-postid='" + postid + "'] > *").hide().fadeIn(100);

          },
          error: function(){ 
                popup("Something went wrong");

          },
          dataType: 'json'
        });

}



function voteReply(post,type){
    var ele = $(post).closest('#status-sec');
    var postid = ele.data()['postid'];
    //var ownerid = ele.data()['ownerid'];
    var replyid = $(post).closest('.reply').data()['postid'];
    var is_club = false;
    var vote = $(post).closest('.reply').data('vote');
    var current_score_ele =  $(post).closest('.reply').find('p').first();
    var score = parseInt(current_score_ele.text());
    var reply_class = $(post).closest('.reply');
    console.log(reply_class);
    console.log(vote);
    $.ajax({
          type: "POST",
          url: '/actions/friend_vote',
          data: { 'vote_type' : type,'post_id' : postid,'reply_id' : replyid,'is_reply' : true},
          success: function(){ 
              if(vote == -1){
                if(type == "up"){
                console.log($(ele).eq(0));
                 $(post).closest('.reply').data('vote',0);
                 $(reply_class).find('#rep_down').eq(0).css('color','gray');
                 current_score_ele.text(score+1);
                } 
              }
              else if(vote == 0){
                if(type == "up"){
                 $(post).closest('.reply').data('vote',1);
                 $(post).children().eq(0).css('color','orange');
                 current_score_ele.text(score+1);

                }
                if(type == "down"){
                 $(post).closest('.reply').data('vote',-1);
                 //console.log($(ele).children().eq(0));
                 $(post).children().eq(0).css('color','blue');
                 current_score_ele.text(score-1);
                }
              }
              else if(vote == 1){
                if(type == "down"){
                 $(post).closest('.reply').data('vote',0);
                   //console.log($(ele).children().eq(0));
                   //console.log($(ele).eq(0).prevAll('a.upvote').first());
                   $(reply_class).find('#rep_up').eq(0).css('color','gray');
                   current_score_ele.text(score-1);


                }
              }
              
                //$(".reply[data-postid='" + replyid + "']").load('/actions/get_replies?post_id='+postid+" .reply[data-postid='" + replyid + "'] > *").hide().fadeIn(700);
          },
          dataType: 'json'
        });
}


function post(userid,networkid){
    console.log("i"+networkid);
    console.log("u" + userid);
        var message = $('#status-text').val();
        var posttype = PostType.WALL_POST;
        console.log(networkid);
        //var networkid = $('#status_text').data('networkid');
        $.ajax({
              type: "POST",
              url: '/actions/post',
              data: { 'message' : message, 'posttype' : posttype,'networkid' : networkid,'user_id' : userid},
              success: function(){
                    var current_page = document.URL;
                    console.log(current_page);
                    $('#status-feed').load(current_page+' #status-feed > *').hide().fadeIn('slow');

                    $('#status-text').val('');
              },
              dataType: 'json'
            });
}





function reply(post){
    var ele = $(post).closest('#status-sec');
    var postid = ele.data()['postid'];
    var message =   $(".reply-box[data-postid='" + postid+ "'] textarea").val();


    console.log(message);
    //var replyid = postid;
    var posttype = PostType.REPLY_POST;

    $.ajax({
          type: "POST",
          url: '/actions/post',
          data: { 'message' : message, 'posttype' : posttype, 'postid' : postid},
          success: function(){      
            hideReply(post);
            loadReplies(post);
          },
          dataType: 'json'
        });

}

function replyreply(post){
    var ele = $(post).closest('#status-sec');
    var postid = ele.data()['postid'];
    var replyid = $(post).closest('.reply').data()['postid'];
    var message =   $(".reply-box[data-postid='" + replyid+ "'] textarea").val();

    var posttype = PostType.REPLY_POST;

    $.ajax({
          type: "POST",
          url: '/actions/post',
          data: { 'message' : message, 'posttype' : posttype, 'postid' : postid,'replyid' : replyid},
          success: function(){      
            hideReply(post);
            loadReplies(post);
          },
          dataType: 'json'
        });
}

function displayReply(post){
    var ele = $(post).closest('#status-sec').data()['postid'];
    $(".reply-box[data-postid='" + ele + "']").slideDown(300);
}

function displayReplyReply(post){
    var ele = $(post).closest('.reply').find('.reply-box').data()['postid'];
    console.log(ele);
    $(".reply-box[data-postid='" + ele + "']").slideDown(300);
}

function hideReply(post){
    $(post).closest('.reply-box').slideUp(300);
}

function hideReplies(ele){
    var ssec = $(ele).closest('#status-sec')
    var nele = ssec.find('.reply-sec');
    $(nele).fadeOut(300);
}
function toggleReplies(ele){
    if(ele.innerHTML == "Show Comments"){
        ele.innerHTML = "Hide Comments";
        loadReplies(ele);
    }
        else{
            ele.innerHTML = "Show Comments";
            hideReplies(ele);
        }
}

function toggleNotifications(){
    var isvis = $('#not-menu-cont').is(":visible");
    // console.log(hid);
    if(isvis == false){
            $.ajax({
              type: "POST",
              url: '/actions/get_nots',
              data: { },
              success: function(){ alert('success');
              },
              dataType: 'json'
            });
            $('#not .icon-globe').load('/ #not .icon-globe > *');
            $('#not .icon-globe').css('color','black');
            // $('#not-menu').hide();
    }
    
     $('#not-menu-cont').fadeToggle();
}

function popup(message) {
        
    // get the screen height and width  
    var maskHeight = $(window).height();  
    var maskWidth = $(window).width();
    
    // calculate the values for center alignment
    var dialogTop =  (maskHeight/3) - ($('#dialog-box').height());  
    var dialogLeft = (maskWidth/2) - ($('#dialog-box').width()/2); 
    
    // assign values to the overlay and dialog box
    // $('#dialog-overlay').css({height:maskHeight, width:maskWidth}).show();
    $('#dialog-box').fadeIn();
    
    // display the message
    $('#dialog-message').html(message);


    setTimeout(function(){
    $('#dialog-box').fadeOut();}, 3000);
}

function submitClub(self){
    var memberform = $(self).find('#memberTags span.tagit-label').eq(1).data('fid');
    var members_li = $(self).find('#memberTags span.tagit-label');
    var admins_li = $(self).find('#adminTags span.tagit-label');

    var length = $(self).find('#memberTags span.tagit-label').length;
    var lengtha = $(self).find('#adminTags span.tagit-label').length;
    var members = "";
    var admins = "";
    for(var i=0;i<length;i++){
        members += members_li.eq(i).data('fid') + ",";
    }
    for(var i=0;i<lengtha;i++){
        admins += admins_li.eq(i).data('fid') + ",";
    }
    var name = $(self).find('input[name="name"]').val();
    var about = $(self).find('#newclubabout').val();
    var priv = checked = $('#publicsw').is(':checked');
    // console.log(about);
        $.ajax({
          type: "POST",
          url: '/actions/new_club',
          data: {'members':members,'name' : name,'about': about,'private' : priv , 'admins' : admins},
          success: function(){ 

            popup("Club created successfully!");
            $('#newclub').fadeOut();

          },
          error:function(){
            popup("something went wrong");
          },
          dataType: 'json'
        });

}

function togglePop(){
    var maskHeight = $(window).height();  
    var maskWidth = $(window).width();
    console.log(maskHeight);
    var dialogTop =  (maskHeight/3) - ($('#newclub').height())-300;  
    var dialogLeft = (maskWidth/2) - ($('#newclub').width()/2);
    // $('#newclub').css({top:50%, left:50%});
    $("#newclub").fadeToggle();

}

function requestMember(clubid){
    
    var action = MemberAction.ADD;

    $.ajax({
        type: "POST",
        url: '/club/members',
        data: {'clubid': clubid,'action' : action},
        success: function(){ 

         // popup("M");
          $("#user-data").load(document.URL+" #user-data > *").hide().fadeIn(100);

        },
        error:function(){
          popup("something went wrong");
        },
        dataType: 'json'
    });
}
function addMember(userid,clubid) {
    
    var action = MemberAction.CONFIRM;

                $.ajax({
              type: "POST",
              url: '/club/members',
              data: {'clubid': clubid,'userid' : userid,'action' : action},
              success: function(){ 

                popup("Member added successfully!");
                $("#Main-Content").load(document.URL+" #Main-Content > *").hide().fadeIn(100);

              },
              error:function(){
                popup("something went wrong");
              },
              dataType: 'json'
            });
}

function sendRequest(element,userid){
      var userstatus = $(element).data()['userstatus'];
      $.ajax({
        type: "POST",
        url: '/actions/respond_friend',
        data: { 'Action' : 1, 'UserStatus' : userstatus , '_id' : userid},
        success: function(){ $('#Main-Content').load(document.URL+' #Main-Content > *');
        },
        dataType: 'json'
      });

}

$("#logo").click(function(){
     // window.location=$(this).find("a").attr("href"); 
     window.location = ("/");
     return false;
});
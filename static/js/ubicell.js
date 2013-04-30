$(document).ready(function() {
         $('#reply-box').hide();
         $('.reply-sec').hide();
         $('#not-menu-cont').hide();
         var availableTags = [];
         var friendIds = [];

        {%for friend in friends%}

            availableTags.push("{{friend['FirstName'].capitalize()}} {{friend['LastName'].capitalize()}}");
            friendIds.push("{{friend['_id']}}");
        {%end%}
         $("#memberTags").tagit({
            fieldName: "members",
    availableTags: availableTags,
    placeholderText: "Members",
    singleField: true,
    beforeTagAdded: function(event, ui) {
        // do something special
        var text = ui.tag.find('span.tagit-label').text();
        var index = $.inArray(text, availableTags);
        if(index < 0){
            return false;
        }
        console.log(ui.tag);
        $(ui.tag.find('span.tagit-label')).data('fid',friendIds[index]);

        return index >= 0;
    }

});
    $("#adminTags").tagit({
        fieldName: "admins",
    availableTags: availableTags,
    placeholderText: "Admins",
    beforeTagAdded: function(event, ui) {
        // do something special
        var text = ui.tag.find('span.tagit-label').text().toLowerCase();
        return $.inArray(text, availableTags) >= 0;
    }

}); 


    console.log(availableTags);
    });

function submitClub(self){
        var memberform = $(self).find('#memberTags').find('li').children().data('fid');
        console.log(memberform);
        console.log($(self).find('#memberTags'));
            // $.ajax({
            //   type: "POST",
            //   url: '/actions/new_club',
            //   data: { },
            //   success: function(){ alert('success');
            //   },
            //   dataType: 'json'
            // });

}
    // {%set c = 'black'%}
    // console.log({{len(actions.core_actions.get_unread_notifications(current_user['_id']['$oid']))}});
    // {%if len(actions.core_actions.get_unread_notifications(current_user['_id']['$oid'])) > 0%}

    //  {%set c = 'orange'%}
    //  $('.notification-count').show();
    // {%end%}
    //  $('.icon-globe').css('color','{{c}}')
     // $('.icon-globe:hover').css('color','orange')


    

    function loadReplies(ele){

        var ssec = $(ele).closest('#Status-sec')
        var nele = ssec.find('.reply-sec');
        var postid = ssec.data()['postid'];
        var ownerid = ssec.data()['ownerid'];
        var checked = !$('.onoffswitch-checkbox').is(':checked');
        if($('.onoffswitch-checkbox').length <= 0){
            checked = false;
        }
        //var postid = 
        $(nele).load('/actions/get_replies?post_id='+postid+'&owner_id='+ownerid+'&is_uni='+checked).hide().fadeIn(300);
    }

    function hideReplies(ele){
        var ssec = $(ele).closest('#Status-sec')
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

    function searchFriends(){
        var query = $('.search_box').val();
        $('head').append('<link rel="stylesheet" type="text/css" href="/static/styles/search.css">');
    //  $('#Main-Content').load("/search?" + $.param({ query : query}) + " #Main-Content > *").hide().fadeIn(700);
        window.location = ("/search?" + $.param({ query : query}));
    }

    function vote(ele,type){
        var postid = $(ele).closest('#Status-sec').data()['postid'];
        var ownerid = $(ele).closest('#Status-sec').data()['ownerid'];
        console.log(postid);
        var element = $(ele).closest('#Status-sec');
        var vote_type = "";
        var is_uni = !$('.onoffswitch-checkbox').is(':checked');
        if($('.onoffswitch-checkbox').length <= 0){
            is_uni = false;
        }
        console.log(is_uni);
        if(type == 'up'){
            vote_type = "up";
        }
        else{
            vote_type = "down";
        }
        $.ajax({
              type: "POST",
              url: '/actions/friend_vote',
              data: { 'vote_type' : vote_type,'post_owner' : ownerid,'post_id' : postid,'is_reply' : "false",'is_uni' : is_uni},
              success: function(){ 
                                        if($('.onoffswitch-checkbox').length <= 0){
            checked = false;
        }
        if(checked){
            $("#Status-sec[data-postid='" + postid + "']").load("/ #Status-sec[data-postid='" + postid + "'] > *").hide().fadeIn(100);

        }
        else{
            $("#Status-sec[data-postid='" + postid + "']").load("/?University=True #Status-sec[data-postid='" + postid + "'] > *").hide().fadeIn(100);

        

        }
              },
              error: function(){ 


              },
              dataType: 'json'
            });
            var checked = $('.onoffswitch-checkbox').is(':checked');
        // if($('.onoffswitch-checkbox').length <= 0){
        //  checked = false;
        // }
  //        if(checked){
  //            $("#Status-sec[data-postid='" + postid + "']").load("/ #Status-sec[data-postid='" + postid + "'] > *").hide().fadeIn(100);

  //        }
  //        else{
  //            $("#Status-sec[data-postid='" + postid + "']").load("/?University=True #Status-sec[data-postid='" + postid + "'] > *").hide().fadeIn(100);

        

  //        }
    }

    function voteReply(post,type){
        var ele = $(post).closest('#Status-sec');
        var postid = ele.data()['postid'];
        var ownerid = ele.data()['ownerid'];
        var replyid = $(post).closest('.reply').data()['postid'];
        var isReply = "true";
        var vote_type = "";
        var is_uni = !$('.onoffswitch-checkbox').is(':checked');
        if($('.onoffswitch-checkbox').length <= 0){
            is_uni = false;
        }
        if(type == 'up'){
            vote_type = "up";
        }
        else{
            vote_type = "down";
        }
        $.ajax({
              type: "POST",
              url: '/actions/friend_vote',
              data: { 'vote_type' : vote_type,'post_owner' : ownerid,'post_id' : postid,'reply_id' : replyid,'is_reply' : isReply,'is_uni' : is_uni},
              success: function(){ alert('success');
              },
              dataType: 'json'
            });
        $(".reply[data-postid='" + replyid + "']").load('/actions/get_replies?post_id='+postid+'&owner_id='+ownerid+'&is_uni='+is_uni+" .reply[data-postid='" + replyid + "'] > *").hide().fadeIn(700);
    }
    function post(){
        {% from constants import * %}
        var message = $('#status_text').val();
        var posttype = parseInt({{PostType.WALL_POST}});
        var is_uni = !$('.onoffswitch-checkbox').is(':checked');
        console.log(posttype);
        $.ajax({
              type: "POST",
              url: '/actions/post',
              data: { 'message' : message, 'posttype' : posttype,'is_uni' : is_uni},
              success: function(){ alert('success');
              },
              dataType: 'json'
            });
        var checked = $('.onoffswitch-checkbox').is(':checked');
        if($('.onoffswitch-checkbox').length <= 0){
            checked = false;
        }
        if(checked){
            $('#Status-Feed').load('/ #Status-Feed > *').hide().fadeIn('slow');
        }
        else{
            $('#Status-Feed').load('/?University=True #Status-Feed > *').hide().fadeIn('slow');
        }
        $('#status_text').val('');

    }

    function reply(post){
        var ele = $(post).closest('#Status-sec');
        var postid = ele.data()['postid'];
        var ownerid = ele.data()['ownerid'];
        var message =   $("#reply-box[data-postid='" + postid+ "'] textarea").val();
        var is_uni = !$('.onoffswitch-checkbox').is(':checked');
        if($('.onoffswitch-checkbox').length <= 0){
            is_uni = false;
        }
        console.log(message);
        //var replyid = postid;
        {% from constants import * %}
        var posttype = parseInt({{PostType.REPLY_POST}});

        $.ajax({
              type: "POST",
              url: '/actions/post',
              data: { 'message' : message, 'posttype' : posttype, 'postid' : postid,'ownerid' : ownerid,'is_uni' : is_uni},
              success: function(){ alert('success');
              },
              dataType: 'json'
            });
        hideReply(post);
        loadReplies(post);

    }

    function replyreply(post){
        var ele = $(post).closest('#Status-sec');
        var postid = ele.data()['postid'];
        var ownerid = ele.data()['ownerid'];
        //console.log(post);
        //console.log(ownerid);
        var replyid = $(post).closest('.reply').data()['postid'];
        //console.log(replyid);
        var message =   $("#reply-box[data-postid='" + replyid+ "'] textarea").val();

        var is_uni = !$('.onoffswitch-checkbox').is(':checked');
        if($('.onoffswitch-checkbox').length <= 0){
            is_uni = false;
        }
        //console.log(message);
        
        {% from constants import * %}
        var posttype = parseInt({{PostType.REPLY_POST}});

        $.ajax({
              type: "POST",
              url: '/actions/post',
              data: { 'message' : message, 'posttype' : posttype, 'postid' : postid,'ownerid' : ownerid,'replyid' : replyid,'is_uni':is_uni},
              success: function(){ alert('success');
              },
              dataType: 'json'
            });
        hideReply(post);
        loadReplies(post);


    }
    function displayReply(post){
        var ele = $(post).closest('#Status-sec').data()['postid'];
        $("#reply-box[data-postid='" + ele + "']").slideDown(300);
    }

    function displayReplyReply(post){
        var ele = $(post).closest('.reply').find('#reply-box').data()['postid'];
        console.log(ele);
        $("#reply-box[data-postid='" + ele + "']").slideDown(300);
    }

    function hideReply(post){
        $(post).closest('#reply-box').slideUp(300);
    }
    function getPosts(){
        var feed=       $.ajax({
              type: "GET",
              url: '/actions/post',
              data: { },
              success: function(){ alert('success');
              },
              dataType: 'json'
            });
        console.log(feed);
    }
$("#logo").click(function(){
     // window.location=$(this).find("a").attr("href"); 
     window.location = ("/");
     return false;
});



$(".onoffswitch-checkbox").click(function(){
     // window.location=$(this).find("a").attr("href"); 
    var checked = $('.onoffswitch-checkbox').is(':checked');
    if(checked){
        $('#Status-Feed').load('/ #Status-Feed > *').hide().fadeIn('slow');
        $('#hhead').html("{{current_user['FirstName'].capitalize()}} {{current_user['LastName'].capitalize()}}");
    }
    else{
        {%import models.University%}
        $('#Status-Feed').load('/?University=True #Status-Feed > *').hide().fadeIn('slow');
        $('#hhead').html("{{uniname}}");

    }
});




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

$(document).ready(function () {

    // if user clicked on button, the overlay layer or the dialogbox, close the dialog  
    $('a.btn-ok, #dialog-overlay, #dialog-box').click(function () {     
        $('#dialog-overlay, #dialog-box').hide();       
        return false;
    });
    
    // if user resize the window, call the same function again
    // to make sure the overlay fills the screen and dialogbox aligned to center    
    $(window).resize(function () {
        
        //only do it if the dialog box is not hidden
        if (!$('#dialog-box').is(':hidden')) popup();       
    }); 
    
    
});

function togglePop(){
    var maskHeight = $(window).height();  
    var maskWidth = $(window).width();
    console.log(maskHeight);
    var dialogTop =  (maskHeight/3) - ($('#newclub').height())-300;  
    var dialogLeft = (maskWidth/2) - ($('#newclub').width()/2);
    // $('#newclub').css({top:50%, left:50%});
    $("#newclub").fadeToggle();

}

//Popup dialog
function popup(message) {
        
    // get the screen height and width  
    var maskHeight = $(window).height();  
    var maskWidth = $(window).width();
    
    // calculate the values for center alignment
    var dialogTop =  (maskHeight/3) - ($('#dialog-box').height());  
    var dialogLeft = (maskWidth/2) - ($('#dialog-box').width()/2); 
    
    // assign values to the overlay and dialog box
    $('#dialog-overlay').css({height:maskHeight, width:maskWidth}).show();
    $('#dialog-box').css({top:dialogTop, left:dialogLeft}).show();
    
    // display the message
    $('#dialog-message').html(message);

}

// $('.notification-count').hide();

$('#logo img').css('cursor', 'pointer');

$('#logo img:hover').css('background', 'gray');

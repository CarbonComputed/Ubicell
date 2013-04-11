


	function getPosts(){
		var feed = $.ajax({
			type: "GET",
			url: '/actions/post',
			data: { },
			success: function(){ alert('success');
		},
		dataType: 'json'
	});
		console.log(feed);
	}

	function reply(post){
		var ele = $(post).closest('#Status-sec');
		var postid = ele.data()['postid'];
		var ownerid = ele.data()['ownerid'];
		var message = 	$("#reply-box[data-postid='" + postid+ "'] textarea").val();

		console.log(message);
		//var replyid = postid;
		{% from constants import * %}
		var posttype = parseInt({{PostType.REPLY_POST}});

		$.ajax({
			type: "POST",
			url: '/actions/post',
			data: { 'message' : message, 'posttype' : posttype, 'postid' : postid,'ownerid' : ownerid},
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
		var message = 	$("#reply-box[data-postid='" + replyid+ "'] textarea").val();


		//console.log(message);
		
		{% from constants import * %}
		var posttype = parseInt({{PostType.REPLY_POST}});

		$.ajax({
			type: "POST",
			url: '/actions/post',
			data: { 'message' : message, 'posttype' : posttype, 'postid' : postid,'ownerid' : ownerid,'replyid' : replyid},
			success: function(){ alert('success');
		},
		dataType: 'json'
	});
		hideReply(post);
		loadReplies(post);


	}

	function loadReplies(ele){

		var ssec = $(ele).closest('#Status-sec')
		var nele = ssec.find('.reply-sec');
		var postid = ssec.data()['postid'];
		var ownerid = ssec.data()['ownerid'];
		//var postid = 
		$(nele).load('/actions/get_replies?post_id='+postid+'&owner_id='+ownerid+'').hide().fadeIn(300);
	}

	function searchFriends(){
		var query = $('.search_box').val();
		$('head').append('<link rel="stylesheet" type="text/css" href="/static/styles/search.css">');
		$('#Main-Content').load("/search?" + $.param({ query : query}) + " #Main-Content > *").hide().fadeIn(700);

	}

	function vote(ele,type){
		var postid = $(ele).closest('#Status-sec').data()['postid'];
		var ownerid = $(ele).closest('#Status-sec').data()['ownerid'];
		console.log(postid);
		var element = $(ele).closest('#Status-sec');
		var vote_type = "";
		
		if(type == 'up'){
			vote_type = "up";
		}
		else{
			vote_type = "down";
		}
		$.ajax({
			  type: "POST",
			  url: '/actions/friend_vote',
			  data: { 'vote_type' : vote_type,'post_owner' : ownerid,'post_id' : postid,'is_reply' : "false"},
			  success: function(){ alert('success');
			  },
			  dataType: 'json'
			});
		$("#Status-sec[data-postid='" + postid + "']").load("/ #Status-sec[data-postid='" + postid + "'] > *").hide().fadeIn(700);
	}

	function voteReply(post,type){
		var ele = $(post).closest('#Status-sec');
		var postid = ele.data()['postid'];
		var ownerid = ele.data()['ownerid'];
		var replyid = $(post).closest('.reply').data()['postid'];
		var isReply = "true";
		var vote_type = "";
		if(type == 'up'){
			vote_type = "up";
		}
		else{
			vote_type = "down";
		}
		$.ajax({
			  type: "POST",
			  url: '/actions/friend_vote',
			  data: { 'vote_type' : vote_type,'post_owner' : ownerid,'post_id' : postid,'reply_id' : replyid,'is_reply' : isReply},
			  success: function(){ alert('success');
			  },
			  dataType: 'json'
			});
		$(".reply[data-postid='" + replyid + "']").load('/actions/get_replies?post_id='+postid+'&owner_id='+ownerid+" .reply[data-postid='" + replyid + "'] > *").hide().fadeIn(700);
	}
	function post(){
		{% from constants import * %}
		var message = $('#status_text').val();
		var posttype = parseInt({{PostType.WALL_POST}});
		console.log(posttype);
		$.ajax({
			  type: "POST",
			  url: '/actions/post',
			  data: { 'message' : message, 'posttype' : posttype},
			  success: function(){ alert('success');
			  },
			  dataType: 'json'
			});

		$('#Status-Feed').load('/ #Status-Feed > *').hide().fadeIn('slow');
		$('#status_text').val('');

	}

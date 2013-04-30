from models.Club import *
from models.User import *
from models.School import *
from models.University import *
from models.Post import *
from models.ProfileImage import * 
from models.Reply import *
import logging
from util import *

logger = logging.getLogger(__name__)



def make_club(ownerid,name,university,about="",members=[],admins=[],private=True,callback=None):
    if len(name) <= 0:
        return 500
    admins = admins
    logger.debug("Name "+ name)
    logger.debug("Admins " + str(admins))
    logger.debug("Members " + str(members))
    if ownerid not in admins:
        admins.append(ownerid)
    if ownerid not in members:
        members.append(ownerid)
    club = Club(Admins=admins,Members=members,About=about,Name=name,University=university,Private=private)
    club.save()
    for userid in members:
        user = User.objects(id=userid).first()
        subc = SubClub(Id=club.id,Name=name)
        user.Clubs.append(subc)
        user.save()
    if callback != None:
        return callback(200)
    return 200


def get_club(clubid,callback=None):
    club = Club.objects(id=clubid).first()
    if callback != None:
        return callback(club)
    return club
    

def del_club(clubid):
    pass

def confirm_member(uid,clubid,userid,callback=None):
    club = Club.objects(id=clubid).first()
    uid = ObjectId(uid)
    userid = ObjectId(userid)
    if uid not in club.Admins:
        if callback != None:
            return callback(500)
        return 500
    if userid in club.MemberRequests:
        club.MemberRequests.remove(userid)
        club.Members.append(userid)
        club.save()
        user = User.objects(id=userid).first()
        subc = SubClub(Id=club.id,Name=club.Name)
        user.Clubs.append(subc)
        user.save()
    else:
        if callback != None:
            return callback(500)
        return 500
    if callback != None:
        return callback(200)
        return 200

def add_member(clubid,userid,callback=None):

    club = Club.objects(id=clubid).first()
    if userid not in club.Members:
        if club.Private:
            club.MemberRequests.append(userid)
            club.save()
        else:
            club.Members.append(userid)
            club.save()
    else:
        if callback != None:
            return callback(500)
        return 500
    if callback != None:
        return callback(200)
        return 200

def del_member(clubid,userid):
    club = Club.objects(id=clubid).first()
    if userid in club.Members:
        club.Members.remove(userid)
        club.save()       
    else:
        if callback != None:
            return callback(500)
        return 500
    if callback != None:
        return callback(200)
        return 200

def ban_member(clubid,userid):
    club = Club.objects(id=clubid).first()
    if userid not in club.BanList:
        club.BanList.append(userid)
        club.save()
    else:
        if callback != None:
            return callback(500)
        return 500
    if callback != None:
        return callback(200)
        return 200

def get_feed(clubid):
    club = Club.objects(id=clubid).first()
    if callback != None:
        return callback(club.Wall)
    return club.Wall

def get_members(clubid):
    club = Club.objects(id=clubid).first()
    if callback != None:
        return callback(club.Members)
    return club.Members

def promote_member(clubid,userid):
    club = Club.objects(id=clubid).first()
    if userid not in club.Admins:
        club.Admins.append(userid)
        club.save()
    else:
        if callback != None:
            return callback(500)
        return 500
    if callback != None:
        return callback(200)
        return 200

def demote_member(clubid,userid):
    club = Club.objects(id=clubid).first()
    if userid in club.Admins:
        club.Admins.remove(userid)
        club.save()       
    else:
        if callback != None:
            return callback(500)
        return 500
    if callback != None:
        return callback(200)
        return 200





def post_wall(userid,message,groupid,commenter=None, postid=None,replyid = None,depth=1,callback=None):
    #TODO : leave link(id) to parent
    if postid is None:
        hotness = ranking.hot(1,0,datetime.datetime.now())

        fid = userid #default writing on own wall
        if commenter != None:
            fid = commenter #someone writing on my wall

        post = Post(id=ObjectId(),FriendId=fid,UserId=userid,Message=message,Time=datetime.datetime.now(),
            Hotness=hotness,Upvotes=1,Downvotes=0,Upvoters=[fid],Downvoters=[])
        club = Club.objects(id=groupid).first()
        #print userid,user.to_mongo()
        club.Wall.append(post)
        club.save()

        # post = {'_id' : ObjectId(),'FriendId' : fid, 'UserId' : ObjectId(userid), 'Message' : message, 'Time' : datetime.datetime.now(),
        # 'Hotness' : hotness,  'Upvotes' : 1, 'Downvotes' : 0,'Upvoters' : [fid],'Downvoters' : []}
        # db.user.update({'_id' : ObjectId(userid)},{'$push' : { 'Wall' : post}})
    else:
        if commenter is None:
            return RespError.DEFAULT_ERROR
        confidence = ranking.confidence(1,0)
        if replyid is None:
            replyid = postid  #first set of comments 
        push_rstr = 'Wall' + ('.$.Reply' )
        reply = Reply(id=ObjectId(),ParentId=replyid,UserId=commenter,Message=message,Time=datetime.datetime.now(),
            Hotness=confidence,Upvotes=1,Downvotes=0,Upvoters=[commenter],Downvoters=[])
        club = Club.objects(id=groupid).first()
        print(club.Wall)
        post = funcs.find(club.Wall,'id',ObjectId(postid))
        post.Reply.append(reply)
        
        club.save()
    if callback != None:
        return callback(200)
    return 200

def get_feed(groupid,includeMe=True,orderBy=None,numResults=60,startNum =1,callback=None):

    logger.info("Retrieving university feed")
    uni = Club.objects(id=groupid)
    if callback != None:
        return callback(uni.first().Wall)
    return uni.first().Wall


def upvote_post(ownerid,userid,postid,callback=None):
    club = Club.objects(id=ownerid,Wall__id=ObjectId(postid)).first()
    userwall = club.Wall
    index = funcs.index(userwall,'id',ObjectId(postid))
    post = club.Wall[index]
    
    upvotes = post.Upvotes
    downvotes = post.Downvotes
    upvoters = post.Upvoters
    downvoters = post.Downvoters
    if ObjectId(userid) in upvoters:
        return UpvoteResp.VOTED_ALREADY
    # user.Wall.remove(post)
    if ObjectId(userid) not in downvoters:
        upvotes += 1
        upvoters.append(ObjectId(userid))
    try:
        downvotes -= 1
        downvoters.remove(ObjectId(userid))
    except ValueError:
        downvotes += 1

    hotness = ranking.hot(upvotes,downvotes,post.Time)
    post.Upvoters = upvoters
    post.Downvoters = downvoters
    post.Upvotes = upvotes
    post.Downvotes = downvotes
    post.Hotness = hotness

    
    club.Wall[index] = post
    club.save()
    if callback != None:
        return callback(200)
    return 200

def downvote_post(ownerid,userid,postid,callback=None):
    club = Club.objects(id=ownerid,Wall__id=ObjectId(postid)).first()
    userwall = club.Wall
    index = funcs.index(userwall,'id',ObjectId(postid))
    post = club.Wall[index]
    

    upvotes = post.Upvotes
    downvotes = post.Downvotes
    upvoters = post.Upvoters
    downvoters = post.Downvoters
    if ObjectId(userid) in downvoters:
        return UpvoteResp.VOTED_ALREADY
    # user.Wall.remove(post)
    
    if ObjectId(userid) not in upvoters:
        downvotes += 1
        downvoters.append(ObjectId(userid))
    try:
        upvotes -= 1
        upvoters.remove(ObjectId(userid))
    except ValueError:
        upvotes += 1
    hotness = ranking.hot(upvotes,downvotes,post.Time)
    post.Upvoters = upvoters
    post.Downvoters = downvoters
    post.Upvotes = upvotes
    post.Downvotes = downvotes
    post.Hotness = hotness
    #print post==user.Wall[index]
    #print post is user.Wall[index]
    
    club.Wall[index] = post
    club.save()
    #post = User.objects(id=userid['$oid'],Wall__id=ObjectId(postid)).first()
    
    if callback != None:
        return callback(200)
    return 200


def upvote_comment(ownerid,userid,postid,replyid,callback=None):
    club = Club.objects(id=ownerid,Wall__id=ObjectId(postid)).first()
    userwall = club.Wall
    post_index = funcs.index(userwall,'id',ObjectId(postid))
    reply_index = funcs.index(club.Wall[post_index].Reply,'id',ObjectId(replyid))
    reply = club.Wall[post_index].Reply[reply_index]
    upvotes = reply.Upvotes
    downvotes = reply.Downvotes
    upvoters = reply.Upvoters
    downvoters = reply.Downvoters

    if ObjectId(userid) in upvoters:
        return UpvoteResp.VOTED_ALREADY
    # user.Wall.remove(post)
    if ObjectId(userid) not in downvoters:
        upvotes += 1
        upvoters.append(ObjectId(userid))
    try:
        downvotes -= 1
        downvoters.remove(ObjectId(userid))
    except ValueError:
        downvotes += 1

    hotness = ranking.confidence(upvotes,downvotes)
    reply.Upvoters = upvoters
    reply.Downvoters = downvoters
    reply.Upvotes = upvotes
    reply.Downvotes = downvotes
    reply.Hotness = hotness
    club.Wall[post_index].Reply[reply_index] = reply
    club.save()
    if callback != None:
        return callback(200)
    return 200

def downvote_comment(ownerid,userid,postid,replyid,callback=None):
    club = Club.objects(id=ownerid,Wall__id=ObjectId(postid)).first()
    userwall = club.Wall
    post_index = funcs.index(userwall,'id',ObjectId(postid))
    reply_index = funcs.index(club.Wall[post_index].Reply,'id',ObjectId(replyid))
    reply = club.Wall[post_index].Reply[reply_index]
    upvotes = reply.Upvotes
    downvotes = reply.Downvotes
    upvoters = reply.Upvoters
    downvoters = reply.Downvoters

    if ObjectId(userid) in downvoters:
        return UpvoteResp.VOTED_ALREADY
    # user.Wall.remove(post)
    
    if ObjectId(userid) not in upvoters:
        downvotes += 1
        downvoters.append(ObjectId(userid))
    try:
        upvotes -= 1
        upvoters.remove(ObjectId(userid))
    except ValueError:
        upvotes += 1

    hotness = ranking.confidence(upvotes,downvotes)
    reply.Upvoters = upvoters
    reply.Downvoters = downvoters
    reply.Upvotes = upvotes
    reply.Downvotes = downvotes
    reply.Hotness = hotness
    club.Wall[post_index].Reply[reply_index] = reply
    club.save()
    if callback != None:
        return callback(200)
    return 200

def get_member_data(clubid,callback=None):
    logger.info("Getting Club Members")
    members = Club.objects(id=clubid).first().Members
    print members
    coll = User._get_collection()
    members = coll.find({'Clubs.Id' : ObjectId(clubid)})
    # print members[0]['FirstName']
    if callback != None:
        return callback(members)
    return members

def get_member_req_data(clubid,callback=None):
    logger.info("Getting Club MemberRequests")
    member_reqs = Club.objects(id=clubid).first().MemberRequests
    print member_reqs
    coll = User._get_collection()
    member_reqs = coll.find({'_id' : {'$in' : member_reqs}})
    if callback != None:
        return callback(member_reqs)
    return member_reqs

@funcs.run_async
def get_replies(userid,powner, postid,orderBy = None,callback=None):
    logger.info("Retrieving Replies")
    #coll = User._get_collection()
    #reps = coll.find({ '_id'  : ObjectId(powner),'Wall._id' : ObjectId(postid)},{'Wall.$.Reply' : 1})[0]['Wall'][0]['Reply']
    print('post',postid)
    print('postowner',powner)
    user = Club.objects(id=userid,Wall__id=ObjectId(postid)).first()
    userwall = user.Wall
    post = funcs.find(userwall,'id',ObjectId(postid))
    print(post.Reply)
    if callback != None:
        return callback(post.Reply)
    return post.Reply

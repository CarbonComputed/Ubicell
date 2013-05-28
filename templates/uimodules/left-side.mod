<div id="left-side-bar">
    <div id="subsidebar">
    <a  href="/university" onclick="#"><h3 id="unih">University</h3></a>    
    <a  href="#" onclick="togglePop();return false;"><h3 id="tpop">Clubs</h3></a>
    <ul class="sidebar">
        {%for club in clubs%}
        <a href="/club?clubid={{club.Id}}"><li>{{club.Name}}</li></a>
        <!-- <a href="#"><li>Events ></li></a> -->
        {%end%}
    </ul>
</div>
</div>
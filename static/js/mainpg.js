$(function(){
	$("#news_win").owlCarousel({
		singleItem:true,
		autoPlay:3000
	});
});

function innerGuide(obj){
	if((obj.id=="about_btn")||(obj.id=="about_btn0")) {
		document.getElementById("guide").innerHTML="<tr><td class='inner_btn' ><a id='about_btn1' href='intro' >"+"项目介绍"+
				"</a></td></tr>"+"<tr><td class='inner_btn'><a id='about_btn2' href='news' >"+"活动记录——导读课"+
				"</a></td></tr>"+"<tr><td class='inner_btn'><a id='about_btn3' href='articles' >"+"读书经验谈"+
				"</a></td></tr>"+"<tr><td class='inner_btn'><a id='about_btn4'>"+"项目拓展"+
				"</a></td></tr>"+"<tr><td class='dead_btn'><a id='join_btn0' onmouseover='innerGuide(this)'>"+"加入我们"+
				"</a></td></tr>";
		return true;
	}
	else if((obj.id=="join_btn")||(obj.id=="join_btn0")) {
		document.getElementById("guide").innerHTML="<tr><td class='dead_btn'><a id='about_btn0' onmouseover='innerGuide(this)'>"+"关于苗苗阅读"+
		"</a></td></tr>"+"<tr><td class='inner_btn'><a id='join_btn1' href='../volunteer/' >"+"加入我们"+
		"</a></td></tr>"+"<tr><td class='inner_btn'><a id='join_btn2' href='feelings'>"+"志愿者心声"+
		"</a></td></tr>"+"<tr><td class='inner_btn'><a id='join_btn3' href='train_classes'>"+"志愿者培训"+
		"</a></td></tr>"+"<tr><td class='inner_btn'><a id='join_btn4'>"+"相关资料"+
		"</a></td></tr>";
		return true;
	}
	else 
		return false;
}

function outerGuide(){
	document.getElementById("guide").innerHTML="<tr><td class='big_btn'><a id='about_btn' onmouseover='innerGuide(this)'>"+"关于苗苗阅读"+
				"</a></td></tr>"+"<tr><td class='big_btn'><a id='join_btn' onmouseover='innerGuide(this)'>"+"加入我们"+
				"</a></td></tr>";
		return true;
}





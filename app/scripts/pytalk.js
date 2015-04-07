function update_related(r) {
    
    $("a.favButton").removeClass("recd");

    for(var i=0; i<r.talks.length; i++) {
        var obj = r.talks[i];
        $("#" + obj ).addClass("recd");
    } 

    //update nav buttons
    var rec_count = r.talks.length;
    $("#recs").text("Recommended (" + rec_count +")");

    return false;
}

$('div').live('pageinit', function(){

    $("a.favButton").click(function(){

        $(this).toggleClass('favd');
        $(this).toggleClass('ui-alt-icon');

        var sel_talks="";
        var fav_count=0;
              $('.favd').each(function() {
                    sel_talks += "," + this.id;
        fav_count += 1;
              });

        //update nav buttons
        $("#favs").text("Favs (" + fav_count +")");

        $.ajax({type: "POST",
                url: "http://localhost:8181/rec",
                data: { t: sel_talks},
                cache: false,
                success: function(resp){
                    update_related(resp);
                }
        });
    });

    $("li a").click(function(){
        $(this).find("p.talk-time").toggle();
        $(this).find("p.li-details").toggleClass('expanded');
    });

    $("#recs").click(function(){
        $("a.favButton:not(.recd)").parent().hide();
        $(".recd").parent().show();
    });

    $("#favs").click(function(){
        $("a.favButton:not(.favd)").parent().hide();
        $(".favd").parent().show();
    });

    $("#allT").click(function(){
        $("li").show();
    });

});
$(document).ready(function(){

});


function createId(that){
    var currentTitle = $(that).val().replace(/[^\w\s]/gi, '-');
    currentTitle = currentTitle.replace(/\s/g, "-");
    currentTitle = currentTitle.toLowerCase();
    if(currentTitle){
        currentTitle = currentTitle + "-" + new Date().getTime();
    }

    $("#identifiant").val(currentTitle);
}

function checkUnicity(that){
    var currentId = $(that).val();
    $.ajax({
    type: "POST",
    url: "/checkId",
    data: JSON.stringify({"identifiant": currentId}),
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function(data){
        if(data.idExist){
            $(that).val("");
            $(".main_container").append("<div class='alert alert-danger'>This id already exist. Please create a new one</div>");
        }else{
            $(".alert.alert-danger").remove();
        }
    },
    failure: function(errMsg) {
        console.log(errMsg);
    }
});
}
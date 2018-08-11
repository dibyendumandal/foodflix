function filter_ingredients() {
    $(document).ready(function(){
        $("#search_button").click(function(){
            document.location.href = "/?ingredients=" + $("#ingredients").val();
        });
    });
}

function next_prev_recipes(recipe_num,ingr_user){
    var recipe_num_int = parseInt(recipe_num, 10);
    $(document).ready(function(){
        $("#prev_button").click(function(){
            recipe_num_int -= 10;
            document.location.href = "/?ingredients=" + ingr_user + "&recipe_num=" + recipe_num_int;
        });
    });
    $(document).ready(function(){
        $("#next_button").click(function(){
            recipe_num_int += 10;
            document.location.href = "/?ingredients=" + ingr_user + "&recipe_num=" + recipe_num_int;
        });
    });
}

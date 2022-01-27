function number_validation(){
    $(".numericOnly").bind('keypress',function (e) {
        if (String.fromCharCode(e.keyCode).match(/[^0-9]/g)) return false;
    });
    $(".floatOnly").bind('keypress',function (e) {
        if (String.fromCharCode(e.keyCode).match(/^[0-9]*.?[0-9]*$/g)) return false;
    });
}

$(document).ready(function(){

     //dynamic table for grant other expenses
    var grant_other_expenses_counter = 0;
    if($('#grant_other_expenses')){
        $("#addGrantOtherExpensesRow").on("click", function () {
            var newRow = $("<tr>");
            var cols = "";

            cols += '<td><input type="number" class="form-control numericOnly" name="num_1" value="20"/></td>';
            cols += '<td><input type="number" class="form-control numericOnly" name="num_2" value="18"/></td>';
            cols += '<td><input type="number" class="form-control numericOnly" name="num_3" value="18"/></td>';

            cols += '<td><input type="button" class="ibtnGOEIDel btn btn-md btn-danger "  value="Delete"></td>';
            newRow.append(cols);
            $("table#grant_other_expenses.order-list").append(newRow);
            grant_other_expenses_counter++;
            number_validation();
        });
    }
    $("table.order-list").on("click", ".ibtnGOEIDel", function (event) {
        $(this).closest("tr").remove();
        grant_other_expenses_counter -= 1
    });


    if($('#list_price').length){
        price = priceCalculation(1)
        if(price){
            $('#list_price_span').html(price)
        }
    }

    function priceCalculation(shape) {
        var list_price = $('#list_price').val()
        if(shape == 1){
            var width_shape_1 = $('#width_shape_1').val()
            var height_shape_1 = $('#height_shape_1').val()
            if(width_shape_1 && height_shape_1 && list_price){
                calculation = (((parseInt(width_shape_1)*parseInt(height_shape_1))/1000000)*parseInt(list_price))
                return calculation
            }
            else{
                return false
            }
        }
        else if(shape == 2){
            var width_shape_2 = $('#width_shape_2').val()
            var height_shape_2 = $('#height_shape_2').val()
            if(width_shape_2 && height_shape_2 && list_price){
                calculation = (((parseInt(width_shape_2)*parseInt(height_shape_2))/1000000)*parseInt(list_price))
                return calculation
            }
            else{
                return false
            }
        }
        else if(shape == 4){
            var width_shape_4 = $('#width_shape_4').val()
            var height_shape_4 = $('#height_shape_4').val()
            var height1_shape_4 = $('#height1_shape_4').val()
            if(width_shape_4 && height_shape_4 && height1_shape_4 && list_price){
                calculation = (( ( ( (parseInt(width_shape_4)+parseInt(height_shape_4)) / 2) * parseInt(height1_shape_4) ) /1000000)*parseInt(list_price))
                return calculation
            }
            else{
                return false
            }
        }

    }

    $(document).on('change', '#width_shape_1,#height_shape_1', function(){
        price = priceCalculation(1)
        if(price){
            $('#list_price_span').html(price)
        }
    })

    $(document).on('change', '#width_shape_2,#height_shape_2', function(){
        price = priceCalculation(2)
        if(price){
            $('#list_price_span').html(price)
        }
    })

    $(document).on('change', '#width_shape_4,#height_shape_4,#height1_shape_4', function(){
        price = priceCalculation(4)
        if(price){
            $('#list_price_span').html(price)
        }
    })



    $(document).on('click', '.format_shape_1', function(){
        $('.f_shape_1').show();
        $('.f_shape_2').hide();
        $('.f_shape_3').hide();
        $('.f_shape_4').hide();
        $('.f_shape_5').hide();
        $('.f_shape_6').hide();
        $('.f_shape_7').hide();
        $('.format_img').removeClass('active');
        $('.format_shape_1').addClass('active');
        price = priceCalculation(1)
        if(price){
            $('#list_price_span').html(price)
        }
    });

    $(document).on('click', '.format_shape_2', function(){
        $('.f_shape_2').show();
        $('.f_shape_1').hide();
        $('.f_shape_3').hide();
        $('.f_shape_4').hide();
        $('.f_shape_5').hide();
        $('.f_shape_6').hide();
        $('.f_shape_7').hide();
        $('.format_img').removeClass('active');
        $('.format_shape_2').addClass('active');
        price = priceCalculation(2)
        if(price){
            $('#list_price_span').html(price)
        }
    });

    $(document).on('click', '.format_shape_3', function(){
        $('.f_shape_3').show();
        $('.f_shape_1').hide();
        $('.f_shape_2').hide();
        $('.f_shape_4').hide();
        $('.f_shape_5').hide();
        $('.f_shape_6').hide();
        $('.f_shape_7').hide();
        $('.format_img').removeClass('active');
        $('.format_shape_3').addClass('active');
    });

    $(document).on('click', '.format_shape_4', function(){
        $('.f_shape_4').show();
        $('.f_shape_1').hide();
        $('.f_shape_2').hide();
        $('.f_shape_3').hide();
        $('.f_shape_5').hide();
        $('.f_shape_6').hide();
        $('.f_shape_7').hide();
        $('.format_img').removeClass('active');
        $('.format_shape_4').addClass('active');
        price = priceCalculation(4)
        if(price){
            $('#list_price_span').html(price)
        }
    });

    $(document).on('click', '.format_shape_5', function(){
        $('.f_shape_5').show();
        $('.f_shape_1').hide();
        $('.f_shape_2').hide();
        $('.f_shape_3').hide();
        $('.f_shape_4').hide();
        $('.f_shape_6').hide();
        $('.f_shape_7').hide();
        $('.format_img').removeClass('active');
        $('.format_shape_5').addClass('active');
    });

    $(document).on('click', '.format_shape_6', function(){
        $('.f_shape_6').show();
        $('.f_shape_1').hide();
        $('.f_shape_2').hide();
        $('.f_shape_3').hide();
        $('.f_shape_4').hide();
        $('.f_shape_5').hide();
        $('.f_shape_7').hide();
        $('.format_img').removeClass('active');
        $('.format_shape_6').addClass('active');
    });

    $(document).on('click', '.format_shape_7', function(){
        $('.f_shape_7').show();
        $('.f_shape_1').hide();
        $('.f_shape_2').hide();
        $('.f_shape_3').hide();
        $('.f_shape_4').hide();
        $('.f_shape_5').hide();
        $('.f_shape_6').hide();
        $('.format_img').removeClass('active');
        $('.format_shape_7').addClass('active');
    });

    $(document).on('click', '.right_side', function(){
        var right_side_val = $(this).val()
        if(right_side_val == '2'){
            $('.right_xy').removeClass('d-none')
        }else{
            $('.right_xy').addClass('d-none')
        }
    })

    $(document).on('click', '.top_side', function(){
        var top_side_val = $(this).val()
        if(top_side_val == '2'){
            $('.top_xy').removeClass('d-none')
        }else{
            $('.top_xy').addClass('d-none')
        }
    })

    $(document).on('click', '.left_side', function(){
        var left_side_val = $(this).val()
        if(left_side_val == '2'){
            $('.left_xy').removeClass('d-none')
        }else{
            $('.left_xy').addClass('d-none')
        }
    })

    $(document).on('click', '.bottom_side', function(){
        var bottom_side_val = $(this).val()
        if(bottom_side_val == '2'){
            $('.bottom_xy').removeClass('d-none')
        }else{
            $('.bottom_xy').addClass('d-none')
        }
    })

     // Cart Submit Function
    var has_submit_address_clicked = false;
    $("#cart_form").on('submit' ,function(e) {
        if (!has_submit_address_clicked){
            has_submit_address_clicked = true;
            e.preventDefault();
            var cart_description = 'Product Desciption here....'
            $('input[name="backend_details"]').val(JSON.stringify(cart_description));
            $(this).submit();
        }
    })

});
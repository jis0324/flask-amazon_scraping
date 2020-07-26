$(document).ready(function () {
  $('#submit_btn').on('click', function() {
    event.preventDefault(); //prevent form submit
    $('.error-section').addClass('hide');
    $('.loading').removeClass('hide');
    $('.detail-section').addClass('hide');
    $('form #amazon_url').prop('disabled', true);
    $('form #submit_btn').prop('disabled', true);
    
    $.post('/', { 'url' : $('#amazon_url').val()}, 
    function(returnedData){
      let return_data = JSON.parse(returnedData);
      
      if (return_data == 'None') {
        $('.error-section').removeClass('hide');
      } else {
        let thumbs_div = '';
        for(let i=0; i < return_data['image_urls'].length; i++) {
          thumbs_div += '<img src="' + return_data['image_urls'][i] + '" class="mb-3">';
        };
        $('.detail-section .thumbs-div').html(thumbs_div)

        let main_img = '<img src="' + return_data['image_urls'][0] + '" class="w-100">';
        $('.detail-section .main-img-div').html(main_img)

        let title = '<h4><strong>' + return_data['name'] + '</strong></h4>';
        $('.detail-section .title-div').html(title)

        let price_div = '<span> Price : </span>';
        price_div += '<span class="text-danger"><strong>' + return_data['price'] + '</strong></span>';
        price_div += '<span><strong>' + return_data['shipping_message'] + '</strong></span>';
        $('.detail-section .price-div').html(price_div)

        let features_div = '<ul>';
        for(let i=0; i < return_data['feature_bullets'].length; i++) {
          features_div += '<li>' + return_data['feature_bullets'][i] + '</li>';
        };
        $('.detail-section .features-div').html(features_div)
        
      }
      $('.detail-section').removeClass('hide');
      $('form #amazon_url').val('');
      $('form #amazon_url').prop('disabled', false);
      $('form #submit_btn').prop('disabled', false);
      $('.loading').addClass('hide');
      
    }).fail(function(){
      console.log("error");
    });

    return false;
  });

  $('.thumbs-div').on('click', 'img', function() {
    $('.detail-section .main-img-div img').attr('src', $(this).attr('src'));
  });
});
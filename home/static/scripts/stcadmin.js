function api_error() {
    alert('An error occured.\nPlease check if your operation completed successfully.\nIf not please try again.')
}

$(document).ready(function() {
  $('.datepicker').datepicker({
    showOtherMonths: true,
    selectOtherMonths: true,
    dateFormat: 'yy-mm-dd'
  });
});

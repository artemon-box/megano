window.onload = () => {
  document.getElementById("id_cart_numbers").style.display = "none";
  document.getElementById("id_cart_price").style.display = "none";
  document.getElementById("id_cart_numbers").value = "none";
  document.getElementById("id_cart_price").value = "none";
  document.getElementById("id_type").addEventListener("change", () => {
    let value = document.getElementById("id_type").value;
    if (value === "c") {
      document.getElementById("id_cart_numbers").style.display = null;
      document.getElementById("id_cart_price").style.display = null;
      document.getElementById("id_categories").style.display = "none";
      document.getElementById("id_categories").value = "none";
      document.getElementById("id_products").style.display = "none";
      document.getElementById("id_products").value = "none";
    } else {
      document.getElementById("id_categories").style.display = null;
      document.getElementById("id_products").style.display = null;
      document.getElementById("id_cart_numbers").style.display = "none";
      document.getElementById("id_cart_numbers").value = "none";
      document.getElementById("id_cart_price").style.display = "none";
      document.getElementById("id_cart_price").value = "none";
    }
  });
  function checkDates() {
    let date_from = document.getElementById("id_start").value;
    let date_to = document.getElementById("id_end").value;
    let element = document.querySelectorAll('.timezonewarning');
    let originalText = document.querySelector('.timezonewarning').innerHTML;  // All тут не нужен
    let saveButtons = document.querySelector('.submit-row')
    let percent = document.getElementById("id_percent");
    let volume = document.getElementById("id_discount_volume");
    // percent.display.style = null;
    // volume.display.style = null;
    if (date_from && date_to) {
      if (date_from > date_to) {
        element[1].style.color = 'red';
        element[1].innerHTML = 'Дата окончания акции не может быть раньше даты её начала!';
        saveButtons.style.display = "none";
      } else {
        element[1].style.color = '';
        element[1].innerHTML = originalText;
        saveButtons.style.display = null;
      }
    }
    if (percent.value != 0) {  // если писать !== почему-то не срабатывает
      volume.style.display = "none";
      // alert('ok')
    } else {
      volume.style.display = null;
    }
    if (volume.value != 0) {  // если писать !== почему-то не срабатывает
      percent.style.display = "none";
      percent.volume = null;
    } else {
      percent.style.display = null;
    }
  }
  setInterval(checkDates, 100);
};
console.log("I am running")

function handleNumberChange() {
  var numberInput = document.getElementById('number_of_hotels');
  var formContainer = document.getElementById('dropdownContainer');
  var formCount = formContainer.childElementCount;

  // Get the desired number of form elements
  var desiredCount = parseInt(numberInput.value);

  // Remove excess form elements if the number decreases
  while (formCount > desiredCount) {
    formContainer.removeChild(formContainer.lastChild);
    formCount--;
  }

  // Add additional form elements if the number increases
  while (formCount < desiredCount) {
    var formElement = document.createElement('div');
    formElement.className = 'mb-3';
    formElement.innerHTML = '<label for="hotel' + (formCount + 1) + '" class="form-label">Hotel ' + (formCount + 1) + ':</label>' +
                            '<select class="form-select" id="hotel' + (formCount + 1) + '" onchange="addPin()">' +
                            '<option selected value="null"> -- select an option -- </option>';

    formElement.innerHTML += '</select>';
    formContainer.appendChild(formElement);

    formCount++;
  }

  getHotels()
}

function getHotels()
{
        // Fetch data and populate select elements
      fetch('/index/data') // Replace '/data' with your Flask route URL
        .then(response => response.json())
        .then(data => {
          var selectElements = document.querySelectorAll('select');
          var place_ids = [];
          selectElements.forEach(select => {
                if (select.value != "null")
                {
                    place_ids.push(select.value)
                }
          });
          console.log(place_ids);
          selectElements.forEach(select => {
              //console.log(select.selectedIndex);
              if (select.selectedIndex == 0)
              {
                select.innerHTML = '<option selected value="null"> -- select an option -- </option>';
                data.hotel_names.forEach(dict => {
                if (!place_ids.includes(dict.place_id))
                {
                    var optionElement = document.createElement('option');
                  optionElement.textContent = dict.name;
                  optionElement.value = dict.place_id;
                  select.appendChild(optionElement);
                }
//                  var optionElement = document.createElement('option');
//                  optionElement.textContent = dict.name;
//                  optionElement.value = dict.place_id;
//                  select.appendChild(optionElement);
                });
              }
              else
              {
                    // need to remove or disable the selected values
              }
          });
        })
        .catch(error => {
          console.error('Error:', error);
        });
}

function addPin()
{
    getHotels();
    var selectElements = document.querySelectorAll('select');
    console.log("start")
    //clear pins first
    selectElements.forEach(select => {
        if (select.value != "null")
        {
            console.log(select.value);// <--place_id to be used to add pin in map
        }
//        if (select.selectedIndex != 0)
//        {
//            data.hotel_names.forEach(name => {
//                var optionElement = document.createElement('option');
//                optionElement.textContent = name;
//                select.appendChild(optionElement);
//                console.log(name);
//            });
//        }
    });
    console.log("end")
}

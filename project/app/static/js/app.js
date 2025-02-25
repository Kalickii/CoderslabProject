document.addEventListener("DOMContentLoaded", function() {
  /**
   * HomePage - Help section
   */
  class Help {
    constructor($el) {
      this.$el = $el;
      this.$buttonsContainer = $el.querySelector(".help--buttons");
      this.$slidesContainers = $el.querySelectorAll(".help--slides");
      this.currentSlide = this.$buttonsContainer.querySelector(".active").parentElement.dataset.id;
      this.init();
    }

    init() {
      this.events();
    }

    events() {
      /**
       * Slide buttons
       */
      this.$buttonsContainer.addEventListener("click", e => {
        if (e.target.classList.contains("btn")) {
          this.changeSlide(e);
        }
      });

      /**
       * Pagination buttons
       */
      this.$el.addEventListener("click", e => {
        if (e.target.classList.contains("btn") && e.target.parentElement.parentElement.classList.contains("help--slides-pagination")) {
          this.changePage(e);
        }
      });
    }

    changeSlide(e) {
      e.preventDefault();
      const $btn = e.target;

      // Buttons Active class change
      [...this.$buttonsContainer.children].forEach(btn => btn.firstElementChild.classList.remove("active"));
      $btn.classList.add("active");

      // Current slide
      this.currentSlide = $btn.parentElement.dataset.id;

      // Slides active class change
      this.$slidesContainers.forEach(el => {
        el.classList.remove("active");

        if (el.dataset.id === this.currentSlide) {
          el.classList.add("active");
        }
      });
    }

    /**
     * TODO: callback to page change event
     */
    changePage(e) {
      e.preventDefault();
      const page = e.target.dataset.page;

      console.log(page);
    }
  }
  const helpSection = document.querySelector(".help");
  if (helpSection !== null) {
    new Help(helpSection);
  }

  /**
   * Form Select
   */
  class FormSelect {
    constructor($el) {
      this.$el = $el;
      this.options = [...$el.children];
      this.init();
    }

    init() {
      this.createElements();
      this.addEvents();
      this.$el.parentElement.removeChild(this.$el);
    }

    createElements() {
      // Input for value
      this.valueInput = document.createElement("input");
      this.valueInput.type = "text";
      this.valueInput.name = this.$el.name;

      // Dropdown container
      this.dropdown = document.createElement("div");
      this.dropdown.classList.add("dropdown");

      // List container
      this.ul = document.createElement("ul");

      // All list options
      this.options.forEach((el, i) => {
        const li = document.createElement("li");
        li.dataset.value = el.value;
        li.innerText = el.innerText;

        if (i === 0) {
          // First clickable option
          this.current = document.createElement("div");
          this.current.innerText = el.innerText;
          this.dropdown.appendChild(this.current);
          this.valueInput.value = el.value;
          li.classList.add("selected");
        }

        this.ul.appendChild(li);
      });

      this.dropdown.appendChild(this.ul);
      this.dropdown.appendChild(this.valueInput);
      this.$el.parentElement.appendChild(this.dropdown);
    }

    addEvents() {
      this.dropdown.addEventListener("click", e => {
        const target = e.target;
        this.dropdown.classList.toggle("selecting");

        // Save new value only when clicked on li
        if (target.tagName === "LI") {
          this.valueInput.value = target.dataset.value;
          this.current.innerText = target.innerText;
        }
      });
    }
  }
  document.querySelectorAll(".form-group--dropdown select").forEach(el => {
    new FormSelect(el);
  });

  /**
   * Hide elements when clicked on document
   */
  document.addEventListener("click", function(e) {
    const target = e.target;
    const tagName = target.tagName;

    if (target.classList.contains("dropdown")) return false;

    if (tagName === "LI" && target.parentElement.parentElement.classList.contains("dropdown")) {
      return false;
    }

    if (tagName === "DIV" && target.parentElement.classList.contains("dropdown")) {
      return false;
    }

    document.querySelectorAll(".form-group--dropdown .dropdown").forEach(el => {
      el.classList.remove("selecting");
    });
  });

  /**
   * Switching between form steps
   */
  class FormSteps {
    constructor(form) {
      this.$form = form;
      this.$next = form.querySelectorAll(".next-step");
      this.$prev = form.querySelectorAll(".prev-step");
      this.$step = form.querySelector(".form--steps-counter span");
      this.currentStep = 1;

      this.$stepInstructions = form.querySelectorAll(".form--steps-instructions p");
      const $stepForms = form.querySelectorAll("form > div");
      this.slides = [...this.$stepInstructions, ...$stepForms];

      this.init();
    }

    /**
     * Init all methods
     */
    init() {
      this.events();
      this.updateForm();
    }

    /**
     * All events that are happening in form
     */
    events() {
      // Next step
      this.$next.forEach(btn => {
        btn.addEventListener("click", e => {
          e.preventDefault();
          const active = document.querySelector('div.active')
          if (this.currentStep === 1){
            const checkboxes = active.querySelectorAll('[name="categories"]')
            const isChecked = Array.from(checkboxes).some(checkbox => checkbox.checked)
            if (isChecked) {
              this.currentStep++;
              this.updateForm();
            }
          }
          else if (this.currentStep === 2){
            const bags = active.querySelector('[name="bags"]')
            if (bags.value !== '' && parseInt(bags.value) !== 0){
              this.currentStep++;
              this.updateForm();
            }
          }
          else if (this.currentStep === 3){
            const organizations = active.querySelectorAll('[name="organization"]')
            const isChecked = Array.from(organizations).some(organization => organization.checked)
            if (isChecked){
              this.currentStep++;
              this.updateForm();
            }
          }
          else if (this.currentStep === 4){
            const inputs = active.querySelectorAll('input')
            let validator = 0
            inputs.forEach(function (e){
              if (e.value === ''){
                validator = 0
              }
              else {
                validator = 1
              }})
            if (validator === 1){
              this.currentStep++;
              this.updateForm();
            }
          }
        });
      });

      // Previous step
      this.$prev.forEach(btn => {
        btn.addEventListener("click", e => {
          e.preventDefault();
          this.currentStep--;
          this.updateForm();
        });
      });

      // Form submit
      this.$form.querySelector("form").addEventListener("submit", e => this.submit(e));
    }

    /**
     * Update form front-end
     * Show next or previous section etc.
     */
    updateForm() {
      this.$step.innerText = this.currentStep;

      this.slides.forEach(slide => {
        slide.classList.remove("active");

        if (slide.dataset.step == this.currentStep) {
          slide.classList.add("active");
        }
      });

      this.$stepInstructions[0].parentElement.parentElement.hidden = this.currentStep >= 6;
      this.$step.parentElement.hidden = this.currentStep >= 6;

      const summary = document.querySelector('.summary')
      const summary_first = summary.querySelectorAll('.summary--text')

      if (this.currentStep === 5){
        const form = this.$form.querySelector("form")
        const formData = new FormData(form)
        for (const item of formData){
          if (item[0] === 'more_info'){
            if (item[1] !== ''){
              summary.querySelector('#more_info').innerText = item[1]
            }
          }
          if (item[1] !== '')
            if (item[0] === 'bags') {
              summary_first[0].innerHTML = item[1] + ' worków do oddania';
            }
            else if (item[0] === 'organization') {
              summary_first[1].innerHTML = 'Dla ' + item[1];
            }
            else if (item[0] === 'address') {
              summary.querySelector('#address').innerText = item[1]
            }
            else if (item[0] === 'city') {
              summary.querySelector('#city').innerText = item[1]
            }
            else if (item[0] === 'postcode') {
              summary.querySelector('#postcode').innerText = item[1]
            }
            else if (item[0] === 'phone') {
              summary.querySelector('#phone').innerText = item[1]
            }
            else if (item[0] === 'date') {
              summary.querySelector('#date').innerText = item[1]
            }
            else if (item[0] === 'time') {
              summary.querySelector('#time').innerText = item[1]
            }
        }}
    }

    /**
     * Submit form
     *
     * TODO: validation, send data to server
     */
    submit(e) {
        e.preventDefault();
        const formData = new FormData(this.$form.querySelector('form'))
        const data = new URLSearchParams(formData)
        fetch('/form/', {
          method: "POST",
          body: data
        })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok')
          }
          return response;
        })
        .then(() => {
          return window.location.href = '/donation-confirm/'
        })
        .catch(error => console.error("Error:", error))
    }
  }
  const form = document.querySelector(".form--steps");
  if (form !== null) {
    new FormSteps(form);
  }

const checkboxesTaken = Array.from(document.getElementsByClassName('archive-checkbox'))
const archiveCheckboxSwitch = document.getElementById('archive')

  if (archiveCheckboxSwitch) {
    archiveCheckboxSwitch.addEventListener('change', function () {
      if (archiveCheckboxSwitch.checked) {
        checkboxesTaken.forEach(e => {
          e.style.display = 'block'
        })
      } else {
        checkboxesTaken.forEach(e => {
          e.style.display = 'none'
        })
      }
    })
  }
});

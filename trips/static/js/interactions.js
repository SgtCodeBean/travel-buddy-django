$(document).ready(function () {
  function showFlash(message, level = "info") {
    const $list = $("ul.messages").empty();
    // you could sanitize here if you care about XSS
    $list.append(`<li class="${level}">${message}</li>`);
    // scroll into view in case it’s off-screen
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  // ──────────── 1) Sidebar & Chat Toggles ────────────
  $(".menu-toggle").click(function () {
    const target = $($(this).data("target"));
    target.toggleClass("hidden");
    $("body").toggleClass("no-scroll", !target.hasClass("hidden"));
  });

  $(".btn-send").click(function () {
    let msg = $(".chat-input input").val().trim();
    if (msg) {
      $('<p class="user-message"></p>').text(msg).appendTo(".chat-messages");
      $(".chat-input input").val("");
    }
  });

  $(document).click(function (e) {
    if (!$(e.target).closest(".sidebar, .menu-toggle, header, footer").length) {
      $(".sidebar:not(.hidden)").addClass("hidden");
      $("body").removeClass("no-scroll");
    }
  });

  // ──────────── 2) Date‑Preference Show/Hide & Validation ────────────
  const form = $("#generate-itinerary-form")[0];
  const $submit = $(form).find('button[type="submit"]');

  function updateRequiredFields() {
    // clear all
    $("#start-date, #end-date, #months, #seasons").prop("required", false);

    // set only the relevant ones
    const mode = $('input[name="date-preference"]:checked').val();
    if (mode === "specific-dates") {
      $("#start-date, #end-date").prop("required", true);
    } else if (mode === "specific-months") {
      $("#months").prop("required", true);
    } else if (mode === "specific-seasons") {
      $("#seasons").prop("required", true);
    }
  }

  function validateForm() {
    updateRequiredFields();
    let ok = true;
    $(form).find("[required]").each(function () {
      if ($(this).is(":visible") && !$.trim($(this).val())) {
        ok = false;
        return false; // break
      }
    });
    $submit.prop("disabled", !ok);
  }

  // initial and on-change hooks
  validateForm();
  $('input[name="date-preference"]').on("change", function () {
    showDefaultFields();
    validateForm();
  });
  $(form).on("input change", "input, select", validateForm);

  // ──────────── 3) AJAX Form Submission ────────────
  $("#generate-itinerary-form").submit(function (e) {
  e.preventDefault();
  const $f = $(this);
  const data = $f.serialize();
  const $msgs = $("ul.messages").empty();

  $.ajax({
    url:     $f.attr("action"),
    type:    "POST",
    data:    data,
    headers: { "X-CSRFToken": $f.find("[name=csrfmiddlewaretoken]").val() },

    success(response) {
      // server‐side validation can return { success: false, errors: [...] }
      if (!response.success) {
        response.errors.forEach(err => {
          $msgs.append(`<li class="error">${err}</li>`);
        });
        window.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }

      // ——— HAPPY PATH ———
      $msgs.empty();  // clear any old messages

      // show chat UI
      $(".chat-messages, .chat-input").removeClass("hidden");
      $f.closest("#trip-preferences").addClass("hidden");

      // user message
      const regions = $("#anywhere-checkbox-input").is(":checked")
        ? ["Anywhere"]
        : $('input[name="region[]"]:checked').map((_,el)=> el.value).get();
      const firstMsg = `Regions: ${regions.join(", ")}\nBudget: $${$("#budget").val()}\nType: ${$("#travel-type").val()}\nPrefs: ${$("#custom-preferences").val()}`;
      $('<p class="user-message">').text(firstMsg).appendTo(".chat-messages");

      // rebuild sidebar
      const $sb = $(".chat-history").empty();
      response.itineraries.forEach(i => {
        $sb.append(`
          <li>
            <div class="chat-item">
              <button class="btn chat-hist-btn">
                <span class="trip-name">${i.name}</span>
              </button>
              <div class="trip-actions">
                <button class="btn save-btn" data-save-url="/trips/save_itinerary/${i.id}/">💾</button>
                <button class="btn delete-btn" data-delete-url="/trips/itineraries/${i.id}/delete/">🗑️</button>
              </div>
            </div>
          </li>`);
      });
      bindSaveDeleteButtons();

      // bot message
      $('<p class="bot-message">').text(response.message).appendTo(".chat-messages");
    },

    error(xhr) {
      const resp = xhr.responseJSON;
      if (resp && resp.errors) {
        resp.errors.forEach(err => {
          $msgs.append(`<li class="error">${err}</li>`);
        });
      } else {
        $msgs.append(`<li class="error">An unexpected error occurred.</li>`);
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  });
});

  // ──────────── 4) Save/Delete Button Binding ────────────
  function bindSaveDeleteButtons() {
    $(".save-btn").off("click").on("click", function () {
      fetch(this.dataset.saveUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val(),
          "X-Requested-With": "XMLHttpRequest"
        }
      }).then(r=>r.json()).then(d => {
        if (d.redirect_url) {
          window.location.href = d.redirect_url;
        } else {
          alert(d.message)
        }
      }).catch(err => console.error(err));
    });

    $(document).off("click", "[data-action='delete']");
    $(document).on("click", "[data-action='delete']", function(e) {
      e.preventDefault();
      const url = this.dataset.deleteUrl;
      const confirmMessage =
          this.dataset.confirmMessage || "Are you sure you want to delete this itinerary?";
      if (!confirm(confirmMessage)) {
        return;
      }
      fetch(url, { method: "POST", headers:{ "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val(),
          "X-Requested-With": "XMLHttpRequest"
        }
      })
        .then(r=>r.json())
        .then(d=>{
          if (d.success) {
            showFlash(d.message, "warning");
            $(this).closest(".itinerary-item, .chat-item, .comment").remove();
          } else {
            showFlash(d.message, "error");
          }
        })
        .catch(()=>showFlash("Network error","error"));
    });
  }
  bindSaveDeleteButtons();

  // ──────────── 5) Search Results (if any) ────────────
  const params = new URLSearchParams(window.location.search);
  const resultsContainer = $("#results-container");
  if (resultsContainer.length) {
    const q = params.get("query");
    resultsContainer.html(
      q && q.toLowerCase()==="japan"
        ? `<ul><li>Trip to Japan: Tokyo, Kyoto, Osaka</li><li>Cherry Blossom Tour in Japan</li></ul>`
        : `<p>No results found for your search. Please try a different keyphrase.</p>`
    );
  }

  // ──────────── 6) Anywhere / Region Checkbox Logic ────────────
  $("#anywhere-checkbox-input").change(function () {
    $(".region-checkbox").prop("checked", this.checked);
  });
  $(".region-checkbox").change(function () {
    $("#anywhere-checkbox-input").prop("checked",
      $(".region-checkbox:checked").length === $(".region-checkbox").length
    );
  });

  // ──────────── 7) Date‐Fields Show/Hide ────────────
  function hideAllFields() {
    $("#specific-dates-fields, #specific-months-fields, #specific-seasons-fields, #no-preference-fields")
      .addClass("hidden");
  }
  function showDefaultFields() {
    const val = $('input[name="date-preference"]:checked').val();
    hideAllFields();
    if (val === "specific-dates")   $("#specific-dates-fields").removeClass("hidden");
    if (val === "specific-months")  $("#specific-months-fields").removeClass("hidden");
    if (val === "specific-seasons") $("#specific-seasons-fields").removeClass("hidden");
    if (val === "no-preference")    $("#no-preference-fields").removeClass("hidden");
  }
  $('input[name="date-preference"]').on("change", showDefaultFields);
  hideAllFields(); showDefaultFields();

  // ──────────── 8) Min‐Value Enforcement ────────────
  ["trip-length-months","trip-length-seasons","trip-length-no-preference","budget"]
    .forEach(id => {
      $(`#${id}`).on("input", function(){
        if (this.value && this.value < 1) this.value = "";
      });
    });
    // ──────────── 9) Sort Button Logic ────────────
    $("#sort-btn").on("click", function () {
      // Check if there are any itinerary items
      if ($("ul.itinerary-list li").length === 0) {
        alert("There\'s no itineraries to sort.");
        return;
      }
      // Continue flipping the sort parameter if items exist
      const params = new URLSearchParams(window.location.search);
      const current = params.get("sort") || "date";
      const next = (current === "budget" ? "date" : "budget");
      params.set("sort", next);
      window.location.search = params.toString();
    });
});
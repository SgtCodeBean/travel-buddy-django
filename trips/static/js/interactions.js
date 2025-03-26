$(document).ready(function () {
  // Toggle Sidebar Visibility
  $(".menu-toggle").click(function () {
    const targetSidebar = $($(this).data("target"));
    targetSidebar.toggleClass("hidden");
    $("body").toggleClass("no-scroll", !targetSidebar.hasClass("hidden"));
  });

  // Add New Chat Message
  $(".btn-send").click(function () {
    let message = $(".chat-input input").val();
    if (message.trim() !== "") {
      $('<p class="user-message"></p>')
        .text(message)
        .appendTo(".chat-messages");
      $(".chat-input input").val("");
    }
  });

  // Close Sidebar by Clicking Outside
  $(document).click(function (event) {
    if (
      !$(event.target).closest(".sidebar, .menu-toggle, header, footer").length
    ) {
      $(".sidebar").each(function () {
        if (!$(this).hasClass("hidden")) {
          $(this).addClass("hidden");
          $("body").removeClass("no-scroll");
        }
      });
    }
  });

  // Show chat messages and chat input when "Generate Itinerary" button is clicked
  $("#generate-itinerary-form").submit(function (event) {
    event.preventDefault(); // Prevent the form from submitting normally

    // Parse the user's input from the form
    let regions = [];
    if ($("#anywhere-checkbox-input").is(":checked")) {
      regions.push("Anywhere");
    } else {
      $('input[name="region[]"]:checked').each(function () {
        regions.push($(this).val());
      });
    }
    let budget = $("#budget").val();
    let travelType = $("#travel-type").val();
    let customPreferences = $("#custom-preferences").val();

    // Create the first message from the user's input
    let firstMessage = `Regions: ${regions.join(
      ", "
    )}\nBudget: $${budget}\nType of Travel: ${travelType}\nCustom Preferences: ${customPreferences}`;

    // Show the chat messages and chat input
    $(".chat-messages").removeClass("hidden");
    $(".chat-input").removeClass("hidden");

    // Hide the form
    $(this).closest(".trip-preferences").addClass("hidden");

    // Display the first message in the chat
    $('<p class="user-message"></p>')
      .text(firstMessage)
      .appendTo(".chat-messages");
  });

  // Handle "Anywhere" checkbox interactions
  $("#anywhere-checkbox-input").change(function () {
    if ($(this).is(":checked")) {
      $(".region-checkbox").prop("checked", true);
    } else {
      $(".region-checkbox").prop("checked", false);
    }
  });

  // Handle region checkboxes interactions
  $(".region-checkbox").change(function () {
    if (!$(this).is(":checked")) {
      $("#anywhere-checkbox-input").prop("checked", false);
    } else if (
      $(".region-checkbox:checked").length === $(".region-checkbox").length
    ) {
      $("#anywhere-checkbox-input").prop("checked", true);
    }
  });
});

// JavaScript to handle search results
document.addEventListener("DOMContentLoaded", function () {
  const params = new URLSearchParams(window.location.search);
  const query = params.get("query");
  const resultsContainer = document.getElementById("results-container");

  if (query && query.toLowerCase() === "japan") {
    resultsContainer.innerHTML = `
    <ul>
        <li>Trip to Japan: Tokyo, Kyoto, Osaka</li>
        <li>Cherry Blossom Tour in Japan</li>
    </ul>
    `;
  } else {
    resultsContainer.innerHTML =
      "<p>No results found for your search. Please try a different keyphrase.</p>";
  }
});

document.querySelectorAll('.delete-btn').forEach(button => {
    button.addEventListener('click', function() {
        const itineraryId = this.getAttribute('data-id');
        fetch(`/delete_itinerary/${itineraryId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.closest('.itinerary-item').remove();
            } else {
                alert('Failed to delete itinerary.');
            }
        });
    });
});
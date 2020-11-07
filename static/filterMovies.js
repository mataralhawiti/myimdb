$(document).ready(function () {
  $("#filering_buttons > *").click(function (v) {
    filterMovies(v.target.id);
  });
});

function filterMovies(button_clicked_id) {
  var rating, cardDiv, tr, td, x;
  rating = button_clicked_id;
  cardDiv = document.getElementsByClassName("shadow-sm");

  for (x = 0; x < cardDiv.length; x++) {
    movieRating = cardDiv[x].getElementsByTagName("strong")[0].innerHTML;

    if (movieRating == rating || rating == "All") {
      cardDiv[x].style.display = "initial";
    } else {
      cardDiv[x].style.display = "none";
    }
  }
}

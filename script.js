function openNav() {
    document.getElementById("sidebar").style.width = "250px";
  }
  
  function closeNav() {
    document.getElementById("sidebar").style.width = "0";
  }

  document.getElementById("searchBloc").addEventListener("keyup", function() {
    let input = this.value.toLowerCase();
    let blocs = document.querySelectorAll("#blocList .bloc");

    blocs.forEach(function(bloc) {
        let text = bloc.textContent.toLowerCase();
        if (text.includes(input)) {
            bloc.style.display = "";
        } else {
            bloc.style.display = "none";
        }
    });
}); 
document.addEventListener("DOMContentLoaded", function () {

    const timer = document.getElementById("timer");
    const answerForm = document.getElementById("answerForm");

    if (!timer) {
        console.log("Timer element not found.");
        return;
    }

    // Get timer value from the HTML data attribute
    let timeLeft = parseInt(
        timer.dataset.timeLimit,
        10
    );

    console.log("Timer found.");
    console.log("Time limit:", timeLeft);

    let submitted = false;


    function updateTimer() {

        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;

        timer.textContent =
            String(minutes).padStart(2, "0") +
            ":" +
            String(seconds).padStart(2, "0");

        if (timeLeft <= 30) {

            timer.classList.add(
                "timer-warning"
            );

        }
    }


    updateTimer();


    const countdown = setInterval(function () {

        if (submitted) {

            clearInterval(countdown);

            return;
        }


        timeLeft--;

        updateTimer();


        if (timeLeft <= 0) {

            clearInterval(countdown);

            submitted = true;

            timer.textContent = "00:00";


            if (answerForm) {

                answerForm.submit();

            }

        }

    }, 1000);


    if (answerForm) {

        answerForm.addEventListener(
            "submit",
            function () {

                submitted = true;

                clearInterval(countdown);

            }
        );

    }


    window.confirmEndInterview = function () {

        const confirmed = confirm(
            "Are you sure you want to end the interview?"
        );


        if (confirmed) {

            submitted = true;

            clearInterval(countdown);

        }


        return confirmed;

    };

});
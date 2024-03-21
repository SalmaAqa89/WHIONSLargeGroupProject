document.addEventListener('DOMContentLoaded', function() {
    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    let currentYear = new Date().getFullYear();
    let currentMonth = new Date().getMonth();

    const monthSelect = document.getElementById("monthSelect");
    const yearSelect = document.getElementById("yearSelect");
    const calendarBody = document.getElementById("calendar").getElementsByTagName("tbody")[0];
    
    // Populate month dropdown
    months.forEach((month, index) => {
        let option = new Option(month, index);
        monthSelect.add(option);
    });

    // Populate year dropdown (10 years back and 10 years forward)
    for (let year = currentYear - 10; year <= currentYear + 10; year++) {
        let option = new Option(year, year);
        yearSelect.add(option);
    }

    monthSelect.value = currentMonth;
    yearSelect.value = currentYear;

    function generateCalendar(month, year) {
        currentMonth = month;
        currentYear = year;
        calendarBody.innerHTML = ''; // Clear the calendar

        let firstDay = new Date(year, month).getDay();
        let daysInMonth = 32 - new Date(year, month, 32).getDate();

        // Generating the days for the calendar
        let date = 1;
        for (let i = 0; i < 6; i++) {
            let row = document.createElement('tr');
            for (let j = 0; j < 7; j++) {
                if (i === 0 && j < firstDay) {
                    let cell = document.createElement('td');
                    let cellText = document.createTextNode('');
                    cell.appendChild(cellText);
                    row.appendChild(cell);
                } else if (date > daysInMonth) {
                    break;
                } else {
                    let cell = document.createElement('td');
                    let cellText = document.createTextNode(date);
                    if (date === new Date().getDate() && year === new Date().getFullYear() && month === new Date().getMonth()) {
                        cell.classList.add('today');
                    }
                    cell.appendChild(cellText);
                    row.appendChild(cell);
                    date++;
                }
            }
            calendarBody.appendChild(row);
            if (date > daysInMonth) {
                break; // Stop making rows if we've finished the days in the month
            }
        }
        document.querySelectorAll('#calendar td').forEach(dayCell => {
            dayCell.addEventListener('click', function() {
                const selectedDay = this.textContent; // Get the day number
                // Check if the dayCell contains a day number to avoid empty cells
                if (selectedDay) {
                    const dateString = `${selectedDay} ${months[month]} ${year}`;
                    document.getElementById('modalText').textContent = `You selected: ${dateString}`;
                    document.getElementById('modal').style.display = 'block'; // Show the modal
                }
            });
        });
    
        // Close the modal logic
        document.querySelector('.close').addEventListener('click', function() {
            document.getElementById('modal').style.display = 'none';
        });
    
        // Clicking outside the modal closes it
        window.addEventListener('click', function(event) {
            if (event.target == document.getElementById('modal')) {
                document.getElementById('modal').style.display = 'none';
            }
        });

    }

    document.getElementById("prevMonth").addEventListener("click", function() {
        if (currentMonth === 0) {
            currentMonth = 11;
            currentYear--;
        } else {
            currentMonth--;
        }
        generateCalendar(currentMonth, currentYear);
        monthSelect.value = currentMonth;
        yearSelect.value = currentYear;
    });

    document.getElementById("nextMonth").addEventListener("click", function() {
        if (currentMonth === 11) {
            currentMonth = 0;
            currentYear++;
        } else {
            currentMonth++;
        }
        generateCalendar(currentMonth, currentYear);
        monthSelect.value = currentMonth;
        yearSelect.value = currentYear;
    });

    document.getElementById("goToDate").addEventListener("click", function() {
        currentMonth = parseInt(monthSelect.value);
        currentYear = parseInt(yearSelect.value);
        generateCalendar(currentMonth, currentYear);
    });

    generateCalendar(currentMonth, currentYear); // Generate the current month calendar
});
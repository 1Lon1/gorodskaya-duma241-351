const API_URL = "http://127.0.0.1:8001";

let token = "";

async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const response = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    });

    const data = await response.json();

    if (!response.ok) {
        document.getElementById("login-message").textContent =
            data.detail || "Ошибка входа";
        return;
    }

    token = data.access_token;

    document.getElementById("login-section").style.display = "none";
    document.getElementById("app-section").style.display = "block";

    loadDeputies();
    loadCommissions();
    loadMeetingCommissionOptions();
    loadMeetings();
    loadAttendanceOptions();
}


async function loadDeputies() {
    const response = await fetch(`${API_URL}/api/deputies`);

    const deputies = await response.json();

    const list = document.getElementById("deputies-list");

    list.innerHTML = "";

    deputies.forEach(deputy => {
        const element = document.createElement("div");

        element.className = "deputy";

        element.innerHTML = `
            <strong>${deputy.full_name}</strong>
            <br>
            Партия: ${deputy.party || "Не указана"}
            <br>
            Округ: ${deputy.district || "Не указан"}
        `;

        list.appendChild(element);
    });

    loadChairmanOptions(deputies);
}


async function createDeputy() {
    const fullName = document.getElementById("full-name").value;
    const party = document.getElementById("party").value;
    const district = document.getElementById("district").value;

    const response = await fetch(`${API_URL}/api/deputies`, {
        method: "POST",

        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },

        body: JSON.stringify({
            full_name: fullName,
            party: party,
            district: district
        })
    });

    const data = await response.json();

    if (!response.ok) {
        document.getElementById("deputy-message").textContent =
            data.detail || "Ошибка";
        return;
    }

    document.getElementById("deputy-message").textContent =
        "Депутат успешно добавлен";

    document.getElementById("full-name").value = "";
    document.getElementById("party").value = "";
    document.getElementById("district").value = "";

    loadDeputies();
}


function loadChairmanOptions(deputies) {
    const select = document.getElementById("commission-chairman");

    select.innerHTML =
        '<option value="">Председатель не выбран</option>';

    deputies.forEach(deputy => {
        const option = document.createElement("option");

        option.value = deputy.id;
        option.textContent = deputy.full_name;

        select.appendChild(option);
    });
}


async function loadCommissions() {
    const response = await fetch(`${API_URL}/api/commissions`);

    const commissions = await response.json();

    const list = document.getElementById("commissions-list");

    list.innerHTML = "";

    commissions.forEach(commission => {
        const element = document.createElement("div");

        element.className = "deputy";

        element.innerHTML = `
            <strong>${commission.name}</strong>
            <br>
            Описание: ${commission.description || "Нет описания"}
            <br>
            Председатель ID: ${commission.chairman_id || "Не назначен"}
        `;

        list.appendChild(element);
    });
}


async function createCommission() {
    const name =
        document.getElementById("commission-name").value;

    const description =
        document.getElementById("commission-description").value;

    const chairman =
        document.getElementById("commission-chairman").value;

    const response = await fetch(`${API_URL}/api/commissions`, {
        method: "POST",

        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },

        body: JSON.stringify({
            name: name,
            description: description,
            chairman_id: chairman
                ? Number(chairman)
                : null
        })
    });

    const data = await response.json();

    if (!response.ok) {
        document.getElementById("commission-message").textContent =
            data.detail || "Ошибка";
        return;
    }

    document.getElementById("commission-message").textContent =
        "Комиссия успешно добавлена";

    document.getElementById("commission-name").value = "";
    document.getElementById("commission-description").value = "";
    document.getElementById("commission-chairman").value = "";

    loadCommissions();
}
async function loadMeetings() {

    const response = await fetch(
        `${API_URL}/api/meetings`
    );

    const meetings = await response.json();

    const list =
        document.getElementById("meetings-list");

    list.innerHTML = "";

    meetings.forEach(meeting => {

        const element =
            document.createElement("div");

        element.className = "deputy";

        element.innerHTML = `
            <strong>${meeting.title}</strong>
            <br>
            Дата: ${meeting.date}
            <br>
            Место: ${meeting.location || "Не указано"}
            <br>
            ID комиссии: ${meeting.commission_id}
        `;

        list.appendChild(element);
    });
}


async function loadMeetingCommissionOptions() {

    const response = await fetch(
        `${API_URL}/api/commissions`
    );

    const commissions = await response.json();

    const select =
        document.getElementById("meeting-commission");

    select.innerHTML =
        '<option value="">Выберите комиссию</option>';

    commissions.forEach(commission => {

        const option =
            document.createElement("option");

        option.value = commission.id;
        option.textContent = commission.name;

        select.appendChild(option);
    });
}


async function createMeeting() {

    const commissionId =
        document.getElementById("meeting-commission").value;

    const title =
        document.getElementById("meeting-title").value;

    const date =
        document.getElementById("meeting-date").value;

    const location =
        document.getElementById("meeting-location").value;

    const response = await fetch(
        `${API_URL}/api/meetings`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },

            body: JSON.stringify({
                commission_id: Number(commissionId),
                title: title,
                date: date,
                location: location
            })
        }
    );

    const data = await response.json();

    if (!response.ok) {

        document.getElementById("meeting-message").textContent =
            data.detail || "Ошибка";

        return;
    }

    document.getElementById("meeting-message").textContent =
        "Заседание успешно добавлено";

    document.getElementById("meeting-title").value = "";
    document.getElementById("meeting-date").value = "";
    document.getElementById("meeting-location").value = "";

    loadMeetings();
}
async function loadAttendanceOptions() {

    const meetingsResponse = await fetch(
        `${API_URL}/api/meetings`
    );

    const meetings = await meetingsResponse.json();

    const meetingsSelect =
        document.getElementById("attendance-meeting");

    meetingsSelect.innerHTML =
        '<option value="">Выберите заседание</option>';

    meetings.forEach(meeting => {

        const option =
            document.createElement("option");

        option.value = meeting.id;

        option.textContent =
            `${meeting.title} — ${meeting.date}`;

        meetingsSelect.appendChild(option);
    });


    const deputiesResponse = await fetch(
        `${API_URL}/api/deputies`
    );

    const deputies = await deputiesResponse.json();

    const deputiesSelect =
        document.getElementById("attendance-deputy");

    deputiesSelect.innerHTML =
        '<option value="">Выберите депутата</option>';

    deputies.forEach(deputy => {

        const option =
            document.createElement("option");

        option.value = deputy.id;
        option.textContent = deputy.full_name;

        deputiesSelect.appendChild(option);
    });
}


async function loadAttendance() {

    const meetingId =
        document.getElementById("attendance-meeting").value;

    if (!meetingId) {

        document.getElementById("attendance-message").textContent =
            "Сначала выберите заседание";

        return;
    }

    const response = await fetch(
        `${API_URL}/api/meetings/${meetingId}/attendance`
    );

    const attendance = await response.json();

    const list =
        document.getElementById("attendance-list");

    list.innerHTML = "";

    attendance.forEach(record => {

        const element =
            document.createElement("div");

        element.className = "deputy";

        const status =
            record.status === "present"
                ? "Присутствовал"
                : "Отсутствовал";

        element.innerHTML = `
            Депутат ID: ${record.deputy_id}
            <br>
            Статус: ${status}
        `;

        list.appendChild(element);
    });
}


async function createAttendance() {

    const meetingId =
        document.getElementById("attendance-meeting").value;

    const deputyId =
        document.getElementById("attendance-deputy").value;

    const status =
        document.getElementById("attendance-status").value;

    if (!meetingId || !deputyId) {

        document.getElementById("attendance-message").textContent =
            "Выберите заседание и депутата";

        return;
    }

    const response = await fetch(
        `${API_URL}/api/meetings/${meetingId}/attendance`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },

            body: JSON.stringify({
                deputy_id: Number(deputyId),
                status: status
            })
        }
    );

    const data = await response.json();

    if (!response.ok) {

        document.getElementById("attendance-message").textContent =
            data.detail || "Ошибка";

        return;
    }

    document.getElementById("attendance-message").textContent =
        "Запись посещаемости добавлена";

    loadAttendance();
}
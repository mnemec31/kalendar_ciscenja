import { useState, useEffect } from "react";
import { Calendar, momentLocalizer } from "react-big-calendar";
import moment from "moment";
import { useNavigate } from "react-router-dom";


import { getAllCalendars } from "./api/getAllCalendar.ts"
import "react-big-calendar/lib/css/react-big-calendar.css";
import UploadButton from "./UploadButton.tsx";
import ImportFromURL from "./ImportFromUrl.tsx";
import { getCallendarById } from "./api/getCalendarById.ts";
import "../index.css"


const localizer = momentLocalizer(moment);

const MyCalendar = () => {
    const [events, setEvents] = useState([]);
    const [token, setToken] = useState("")
    const [trigger, setTrigger] = useState(false)
    const navigate = useNavigate();
    const colors = [
        "#BDB2FF",
        "#AEDCF9",
        "#FFD6A5",
        "#CAFFBF",
        "#A0C4FF",
        "#FFADAD",
        "#FDFFB6",
        "#FFC6FF",
    ]

    const handleSelectEvent = async (event: any) => {
        await getCallendarById(token, event.calendar)
    }

    const handleLogout = () => {
        localStorage.removeItem("access_token");
        navigate("/login");
    }

    useEffect(() => {
        const fetchEvents = async () => {
            try {
                const token = localStorage.getItem("access_token")
                if (!token) return

                setToken(token)
                const data = await getAllCalendars(token);
                const dateFormat = "YYYY-MM-DD";
                let mapped_events: any = [];

                for (const cal of data) {
                    for (const event of cal.events) {
                        mapped_events.push({
                            start: moment(event.date_start, dateFormat).toDate(),
                            end: moment(event.date_end, dateFormat).add("days", 1).toDate(),
                            title: `${cal.name}: ${event.summary}`,
                            color: colors[cal.id % colors.length],
                            calendar: `${cal.id}`,
                        });
                    }

                    for (const clean_date of cal.cleaning_dates) {
                        mapped_events.push({
                            start: moment(clean_date.date, dateFormat).toDate(),
                            end: moment(clean_date.date, dateFormat).add("days", 1).toDate(),
                            title: `🧼 Cleaning time: ${cal.name}`,
                            color: "#ffe5ec",
                            textColor: "#000",
                            calendar: `${cal.id}`,
                            id: cal.id
                        });
                    }
                }

                setEvents(mapped_events);
            } catch (err) {
                console.error("Error fetching events:", err instanceof Error ? err.message : 'Unknown error');
            }
        };

        fetchEvents();
    }, [trigger]);

    return (
        <div className="App">
            <div className="flexContainer">
                <h1>🧼 Cleaning calendar</h1>
                <button className="uploadButton" onClick={handleLogout}>Logout</button>
            </div>
            <div className="uploadsDiv">
                <UploadButton token={token} setTrigger={setTrigger} />
                <ImportFromURL token={token} setTrigger={setTrigger} />
                <p>If you want to export original ICS file for calendar, just click on it</p>
            </div>
            <Calendar
                localizer={localizer}
                defaultDate={new Date()}
                defaultView="month"
                events={events}
                onSelectEvent={handleSelectEvent}
                style={{ height: "100vh" }}
                eventPropGetter={(event: any) => ({
                    style: {
                        backgroundColor: event.color || "#f0f0f0",
                        color: event.textColor || "#000"
                    }
                })}
            />
        </div>
    );
};

export default MyCalendar;

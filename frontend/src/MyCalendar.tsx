import { useState, useEffect } from "react";
import { Calendar, momentLocalizer } from "react-big-calendar";
import toast, { Toaster } from "react-hot-toast"
import moment from "moment";

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
    const colors = [
        "#F5F5DC",
        "#FED5CF",
        "#F1B598",
        "#D3C7E6",
        "#f9c74f",
        "#FFDAB9",
        "#FFFACD",
        "#277da1",
    ]

    const handleSelectEvent = async (event) => {
        console.log(event.calendar)
        await getCallendarById(token, event.calendar)
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

                console.log(data);

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
                        console.log(clean_date)
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

                console.log("Mapped events: ", mapped_events);
                setEvents(mapped_events);
            } catch (err) {
                console.error("Error fetching events:", err instanceof Error ? err.message : 'Unknown error');
            }
        };

        fetchEvents();
    }, [trigger]);

    return (
        <div className="App">
            <Toaster
                position="bottom-center"
                reverseOrder={false}
            />

            <h1>🧼 Clean my apartment calendar</h1>
            <div className="uploadsDiv">
                <UploadButton token={token} setTrigger={setTrigger} />
                <ImportFromURL token={token} setTrigger={setTrigger} />
            </div>

            <Calendar
                localizer={localizer}
                defaultDate={new Date()}
                defaultView="month"
                events={events}
                onSelectEvent={handleSelectEvent}
                style={{ height: "100vh" }}
                eventPropGetter={(event) => ({
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

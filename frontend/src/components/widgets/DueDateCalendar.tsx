"use client"

import {Calendar} from "@/components/ui/calendar.tsx";
import {DayModifiers, ModifiersStyles} from "react-day-picker";
import {CSSProperties, useEffect, useState} from "react";
import {AccountDates} from "@/types.ts";

const DueDateCalendar = () => {
  
  const [dueDates, setDueDates] = useState<{ [id: string] : AccountDates; }>({});
  const [month, setMonth] = useState<Date>(new Date());
  
  useEffect(() => {
    updateDates()
  }, []);
  async function updateDates() {
    await onCalendarMonthChange(new Date())
  }
  
  function getModifiers(): DayModifiers {
    const modifiers: { [cls: string]: Date[] } = {
      dueDates: Object.values(dueDates).map(x => new Date(x.due)),
      statementDates: Object.values(dueDates).map(x => new Date(x.statement))
    }

    for (const [key, value] of Object.entries(dueDates)) {
      modifiers["cal-acc-" + key] = [new Date(value.due), new Date(value.statement)]
    }

    return modifiers
  }

  function getModifiersStyles(): ModifiersStyles {
    const modifiers: { [cls: string]: CSSProperties } = {}

    for (const [key, value] of Object.entries(dueDates)) {
      modifiers["cal-acc-" + key] = {
        background: value.color,
        borderColor: value.color
      }
    }

    return modifiers
  }

  async function onCalendarMonthChange(month: Date) {
    const response = await fetch("/api/dates/" + month.getFullYear() + "/" + (month.getMonth()+1))
    const dueDates = await response.json() as { [id: string] : AccountDates; }
    setDueDates(dueDates)
    setMonth(month)
  }

  return (
    <Calendar
        month={month}
        onMonthChange={onCalendarMonthChange}
        modifiers={getModifiers()}
        modifiersStyles={getModifiersStyles()}
        modifiersClassNames={{
          dueDates: "cal-due",
          statementDates: "cal-statement"
        }}
    />
  )
}

export default DueDateCalendar
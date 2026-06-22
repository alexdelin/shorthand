export function getDateString(dateString: string): string {
    // Expects a 10-character ISO-Format date string
    const utcDate = new Date(dateString);
    const options: Intl.DateTimeFormatOptions = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        timeZone: 'UTC'
    };
    return utcDate.toLocaleDateString('en-US', options);
}


export function getDateTimeString(utcDatetimeString: string): string {
    if (!utcDatetimeString.includes('Z') && !utcDatetimeString.includes('UTC') && !utcDatetimeString.includes('+00:00')) {
        utcDatetimeString += 'Z'
    }
    const utcDatetime = new Date(utcDatetimeString);
    const dateOptions: Intl.DateTimeFormatOptions = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric'
    };
    const timeOptions: Intl.DateTimeFormatOptions = {
        hour: 'numeric',
        minute: '2-digit'
    };
    return utcDatetime.toLocaleDateString('en-US', dateOptions) + ' ' + utcDatetime.toLocaleTimeString('en-US', timeOptions);
}

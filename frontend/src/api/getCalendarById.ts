export const getCallendarById = async (token: string, id: string) => {
  try {
    const response = await fetch(`http://127.0.0.1:8000/calendars/${id}`, {
      method: 'GET',
      headers: {
        authorization: `Bearer ${token}`
      }
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const blob = await response.blob();

    // Create a download link and click it programmatically
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `calendar_${id}.ics`
    document.body.appendChild(link);
    link.click();

    // Clean up and remove the link
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);

  } catch (error) {
    throw new Error(
      `Caught error! Error: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
};

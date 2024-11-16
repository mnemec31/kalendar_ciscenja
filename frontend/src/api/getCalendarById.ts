export const getCallendarById = async (token: string, id: string) => {
  try {
    const response = await fetch(`http://127.0.0.1:3107/calendars/${id}`, {
      method: 'GET',
      headers: {
        authorization: `Bearer ${token}`
      }
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const blob = await response.blob();

    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `calendar_${id}.ics`
    document.body.appendChild(link);
    link.click();

    if (link.parentNode) link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);

  } catch (error) {
    throw new Error(
      `Caught error! Error: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
};

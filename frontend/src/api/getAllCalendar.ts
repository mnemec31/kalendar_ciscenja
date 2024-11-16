export const getAllCalendars = async (token: string) => {
  try {
    const response = await fetch('http://127.0.0.1:3107/calendars/', {
      method: 'GET',
      headers: {
        authorization: `Bearer ${token}`
      }
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    throw new Error(
      `Caught error! Error: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
};

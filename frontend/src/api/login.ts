export const login = async (credentials: {
  username: string,
  password: string
}) => {
  try {
    const response = await fetch("http://127.0.0.1:8000/token/", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: new URLSearchParams({
        username: credentials.username,
        password: credentials.password
      })
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

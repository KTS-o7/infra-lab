export const handler = async (event) => {
  return {
    message: `Hello, ${event.name}`
  };
};
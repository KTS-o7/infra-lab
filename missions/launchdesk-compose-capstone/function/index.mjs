export const handler = async (event) => {
  const body = typeof event.body === 'string' ? JSON.parse(event.body) : event.body;
  return {
    statusCode: 200,
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      orderId: body.orderId,
      item: body.item,
      processed: true
    })
  };
};
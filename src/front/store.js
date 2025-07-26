export const initialStore = () => {
  return{
    message: null,
    todos: [
      {
        id: 1,
        title: "Make the bed",
        background: null,
      },
      {
        id: 2,
        title: "Do my homework",
        background: null,
      }
    ],
    token: localStorage.getItem("token") || null,
  }
};

export default function storeReducer(store, action = {}) {
  switch(action.type){
    case 'set_hello':
      return {
        ...store,
        message: action.payload
      };

    case 'set_about':

      const about = action.payload

      return {
        ...store,
        about: about      // mantengo todo pero cambio about en blanco (lo de arriba)(el de azul son los datos que vienen)
      };

    case 'set_dashboard':

      const dashboard = action.payload

      return {
        ...store,
        planets: dashboard
      };

    case 'login':
      return {
        ...store,
        token: action.payload,
      };

    case 'logout':
      return {
        ...store,
        token: localStorage.getItem("token") || null,
      };

    default:
      throw Error('Unknown action.');
  }    
};
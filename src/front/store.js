export const initialStore = () => {
  return{
    message: null,
    token: localStorage.getItem("token") || null,
    profileAvatar: null,
    dashboard: null
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
        dashboard: dashboard
      };

    case 'login':

      const token = action.payload
      
      return {
        ...store,
        token: token,
      };

    case 'logout':
      return {
        ...store,
        token: localStorage.getItem("token") || null,
      };

    case 'ADD_AVATAR':
      return {
        ...store,
        profileAvatar: action.payload
      }

    default:
      throw Error('Unknown action.');
  }    
};
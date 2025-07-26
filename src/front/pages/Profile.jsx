import { useEffect, useState } from "react"
import useGlobalReducer from "../hooks/useGlobalReducer"
import { Link, useNavigate } from "react-router-dom"

const initialProfileState = {
    full_name: '',
    email: '',
    phone_number: '',
    // farm_location: '',
    // farm_name: '',
    farms: [],          // lista de campos    
    avatar: '',
}

export const Profile = () => {

    const { dispatch, store } = useGlobalReducer()

    const navigate = useNavigate()

    const [profileForm, setProfileForm] = useState(initialProfileState);

    const [newFarm, setNewFarm] = useState({
        farm_name: '',
        farm_location: ''
    });

    // const [isLoading, setIsLoading] = useState(false);

    const handleInputChange = ({ target }) => {
        setProfileForm({
            ...profileForm,
            [target.name]: target.value
        })
    };


    const fetchUserProfile = async () => {
        const token = localStorage.getItem("token"); // Donde guardo mi token JWT (lo puedo ver en DevTools)

        if (!token) {
            console.error("No hay token disponible");
            return;
        }

        try {
            const urlBackend = import.meta.env.VITE_BACKEND_URL;
            const response = await fetch(`${urlBackend}/api/profile`, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            console.log("TOKEN ENVIADO:", token);

            if (!response.ok) {
                throw new Error("Error al obtener el perfil");
            }

            const data = await response.json();
            console.log("Datos del perfil:", data);

            setProfileForm(data);  // esto llenará todos los campos

        } catch (error) {
            console.error("Error al conectarse con el backend:", error.message);
        }
    };

    useEffect(() => {
        fetchUserProfile();
    }, []);

    const handleAddFarm = async () => {
        const token = localStorage.getItem("token");

        if (!token) {
            alert("Usuario no autenticado");
            return;
        }

        if (!newFarm.farm_name || !newFarm.farm_location) {
            alert("Debes completar ambos campos");
            return;
        }

        try {
            const urlBackend = import.meta.env.VITE_BACKEND_URL;
            const response = await fetch(`${urlBackend}/api/farms`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(newFarm)
            });

            const data = await response.json();

            if (response.ok) {
                alert("Campo registrado correctamente");
                setNewFarm({ farm_name: '', farm_location: '' });
                fetchUserProfile();         // actualiza perfil con el nuevo huerto
            } else if (response.status === 409) {
                alert("Ya existe una huerto con ese nombre o ubicación");
            } else {
                alert(data.error || "Error al registrar el campo");
            }

        } catch (error) {
            console.error("Error al registrar campo:", error);
            alert("Error de conexión");
        }
    };


    const handleDeleteFarm = async (farmId) => {
        const confirmDelete = window.confirm("¿Estás seguro de que quieres eliminar esta granja?");
        if (!confirmDelete) return;

        const token = localStorage.getItem("token");
        const urlBackend = import.meta.env.VITE_BACKEND_URL;

        try {
            const response = await fetch(`${urlBackend}/api/farms/${farmId}`, {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });

            const data = await response.json();

            if (response.ok) {
                alert("Huerto eliminado correctamente");
                fetchUserProfile();             // Refresca los datos del perfil
            } else {
                alert(`Error al eliminar el huerto: ${data.error || response.statusText}`);
            }
        } catch (error) {
            console.error("Error al eliminar el huerto:", error.message);
            alert("Error de conexión al eliminar el huerto");
        }
    };


    return (

        <div className="container py-5">
            <h2 className="mb-4">Perfil</h2>
            <form className="row" style={{ border: "1px solid red" }}>
                {/* Avatar */}
                <div className="col-sm-4 col-md-4" style={{ border: "1px solid red" }}>
                    <img
                        src={profileForm.avatar || "https://avatar.iran.liara.run/public/4"}
                        onError={(event) => event.target.src = "https://avatar.iran.liara.run/public/4"}
                        className="img-fluid rounded m-auto"
                        alt="Imagen de Perfil"
                    />
                </div>

                {/* Datos personales */}
                <div className="col-sm-8 col-md-8" style={{ border: "1px solid red" }}>
                    {/* Parte texto */}

                    <div className="mb-3">
                        <label htmlFor="fullName" className="fw-bold form-label">Nombre</label>
                        <div className="input-group">
                            <input
                                type="text"
                                className="form-control"
                                id="fullName"
                                placeholder="nombre"
                                name="full_name"
                                value={profileForm.full_name}
                                onChange={handleInputChange}
                            />
                        </div>
                    </div>

                    <div className="mb-3">
                        <label htmlFor="phone" className="fw-bold form-label">Teléfono</label>
                        <div className="input-group">
                            <input
                                type="tel"
                                className="form-control"
                                id="phone"
                                placeholder="Número de Teléfono"
                                name="phone_number"
                                value={profileForm.phone_number}
                                onChange={handleInputChange}
                            />
                        </div>
                    </div>

                    <div className="mb-3">
                        <label htmlFor="email" className="fw-bold form-label">Email</label>
                        <div className="input-group">
                            <input
                                type="email"
                                className="form-control"
                                id="email"
                                placeholder="email"
                                name="email"
                                value={profileForm.email}
                                onChange={handleInputChange}
                            />
                        </div>
                    </div>

                    {profileForm.farms && profileForm.farms.length > 0 && (
                        <div className="mt-4">
                            <h5>Mis Campos</h5>
                            <ul className="list-group">
                                {profileForm.farms.map(farm => (
                                    <li
                                        key={farm.id}
                                        className="list-group-item d-flex justify-content-between align-items-center"
                                    >
                                        <div>
                                            <strong>{farm.farm_name}</strong> - {farm.farm_location}
                                        </div>
                                        <button
                                            className="btn btn-outline-danger btn-sm rounded-circle"
                                            style={{ width: "30px", height: "30px", padding: "0" }}
                                            onClick={() => handleDeleteFarm(farm.id)}
                                            title="Eliminar Huerto"
                                            type="button"
                                        >
                                            <span style={{ fontWeight: "bold" }}>X</span>
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    <div className="mb-3">
                        <label className="fw-bold form-label">Registrar Nuevo Campo</label>
                        <div className="input-group mb-2">
                            <input
                                type="text"
                                className="form-control"
                                placeholder="Nombre del campo"
                                name="farm_name"
                                value={newFarm.farm_name}
                                onChange={(event) =>
                                    setNewFarm({ ...newFarm, farm_name: event.target.value })
                                }
                            />
                        </div>
                        <div className="input-group mb-2">
                            <input
                                type="text"
                                className="form-control"
                                placeholder="Ubicación del campo"
                                name="farm_location"
                                value={newFarm.farm_location}
                                onChange={(event) =>
                                    setNewFarm({ ...newFarm, farm_location: event.target.value })
                                }
                            />
                        </div>
                        <button 
                            className="btn btn-success"
                            type="button"
                            onClick={handleAddFarm}
                        >
                            Agregar Campo
                        </button>
                    </div>



                    {/*<div className="mb-3">
                        <label htmlFor="farmLocation" className="fw-bold form-label">Ubicación del campo</label>
                        <div className="input-group">
                            <input
                                type="text"
                                className="form-control"
                                id="farmLocation"
                                placeholder="Ubicación"
                                name="farm_location"
                                value={profileForm.farm_location}
                                onChange={handleInputChange}
                            />
                        </div>
                    </div>

                    <div className="mb-3">
                        <label htmlFor="farmName" className="fw-bold form-label">Nombre del campo</label>
                        <div className="input-group">
                            <input
                                type="text"
                                className="form-control"
                                id="farmName"
                                placeholder="Nombre campo"
                                name="farm_name"
                                value={profileForm.farm_name}
                                onChange={handleInputChange}
                            />
                        </div>
                    </div>*/}
                </div>

                {/* botones */}

                <div className="col-md-12">
                    <ul className="list-unstyled">
                        <li className="my-2">
                            <button
                                type="submit"
                                className="btn btn-success "
                                disabled={true}
                            >
                                <Link className="text-white text-decoration-none">
                                    Registro Fitosanitario
                                </Link>
                            </button>
                        </li>

                        <li className="my-2">
                            <button
                                type="submit"
                                className="btn btn-success "
                                disabled={true}
                            >
                                <Link className="text-white text-decoration-none">
                                    Registro Nutricional
                                </Link>
                            </button>
                        </li>

                        {/* <li className="my-2">
                                <button
                                    type="submit"
                                    className="btn btn-success "
                                    disabled= {true}
                                >
                                    <Link className="text-white text-decoration-none">
                                        Registro Climatico
                                    </Link>
                                </button>
                            </li> */}

                        <li className="my-2">
                            <button
                                type="submit"
                                className="btn btn-success "
                                disabled={true}
                            >
                                <Link className="text-white text-decoration-none">
                                    Mapa del Huerto
                                </Link>
                            </button>
                        </li>
                    </ul>

                </div>
            </form>
        </div>
    )
};
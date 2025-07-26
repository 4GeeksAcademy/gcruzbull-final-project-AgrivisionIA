import { useEffect, useState } from "react"
import useGlobalReducer from "../hooks/useGlobalReducer"
import { Link, useNavigate } from "react-router-dom"

const initialProfileState = {
    full_name: '',
    email: '',
    phone_number: '',
    farm_location: '',
    farm_name: '',
    avatar: '',
}

export const Profile = () => {

    const { dispatch, store } = useGlobalReducer()

    const navigate = useNavigate()

    const [profileForm, setProfileForm] = useState(initialProfileState);

    // const [isLoading, setIsLoading] = useState(false);

    const handleInputChange = ({ target }) => {
        setProfileForm({
            ...profileForm,
            [target.name]: target.value
        })
    };


    const fetchUserProfile = async () => {
        const token = localStorage.getItem("token"); // o donde guardes tu JWT

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


    return (

        <div className="container py-5">
            <h2 className="mb-4">Perfil</h2>
            <form className="row" style={{ border: "1px solid red" }}>
                {/* Avatar */}
                <div className="col-sm-4 col-md-4" style={{ border: "1px solid red" }}>
                    <img
                        src={profileForm.avatar || "https://avatar.iran.liara.run/public/4"}
                        className="img-fluid rounded m-auto"
                        alt="Imagen de Perfil"
                    />
                    {/*<img
                        src="https://avatar.iran.liara.run/public/4"
                        value={profileForm.avatar}
                        onChange={handleInputChange}
                        className="img-fluid rounded m-auto"
                        alt="Imagen de Perfil"
                    />*/}
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

                    <div className="mb-3">
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
                    </div>
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
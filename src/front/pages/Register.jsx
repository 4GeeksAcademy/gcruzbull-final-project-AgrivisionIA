import { useState } from "react"
import useGlobalReducer from "../hooks/useGlobalReducer"
import { Link, useNavigate } from "react-router-dom"

const initialStateRegister = {
    full_name: '',
    email: '',
    phone_number: '',
    password: '',
    avatar: '',
    acceptTerms: false,
}

export const Register = () => {

    const { dispatch, store } = useGlobalReducer()

    const navigate = useNavigate()

    const [formData, setFormData] = useState(initialStateRegister);    // es lo que voy a mandar en el body

    const [showPassword, setShowPassword] = useState(false);

    const [isLoading, setIsLoading] = useState(false);

    const handleInputChange = (event) => {

        if (event.target.name === "avatar") {
            setFormData((currentFormData) => ({
                ...currentFormData,
                avatar: event.target.files[0],  // archivo, no string
            }));
            return;
        }

        const { name, value, type, checked } = event.target;
        setFormData((currentFormData) => ({
            ...currentFormData,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (event) => {     // asegurarme que el handleInputChange (controla el imput y envia eventos) mande todo bien a formdata 
        event.preventDefault()

        if (!formData.acceptTerms) {
            alert('Debes aceptar los términos y condiciones');
            return;
        }
        setIsLoading(true);

        if (!formData.full_name || !formData.email || !formData.phone_number || !formData.password) {
            alert("Todos los campos son obligatorios");
            return;
        }

        try {
            const urlBackend = import.meta.env.VITE_BACKEND_URL;

            const formDataToSend = new FormData();      // estoy creando un molde del formulario formData
            formDataToSend.append("full_name", formData.full_name);     // append(key, value)
            formDataToSend.append("email", formData.email);
            formDataToSend.append("phone_number", formData.phone_number);
            formDataToSend.append("password", formData.password);
            if (formData.avatar) {
                formDataToSend.append("avatar", formData.avatar);
            }

            const response = await fetch(`${urlBackend}/api/register`, {
                method: "POST",
                body: formDataToSend
            });

            const responseData = await response.json();

            if (response.status === 201) {
                alert("Usuario registrado exitosamente. Redirigiendo al login...");
                setFormData(initialStateRegister);
                setTimeout(() => {
                    navigate("/login");
                }, 2000);
            } else if (response.status === 400) {
                alert(responseData.error || "El usuario ya existe o datos inválidos");
            } else {
                alert(responseData.error || "Error al registrar el usuario, intente nuevamente");
            }

        } catch (error) {
            console.error("Error en la petición:", error);
            alert("Error de conexión.");
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <div className="min-vh-100 d-flex align-items-center bg-light">
            <div className="container py-5">
                <div className="row justify-content-center">
                    <div className="col-md-6 col-lg-5">
                        <div className="card shadow-sm border-0 rounded-4">
                            <div className="card-body p-4">
                                {/* Logo y título */}
                                <div className="text-center mb-4">
                                    <i className="fas fa-leaf fa-2x text-success mb-2"></i>
                                    <h1 className="h4 fw-bold text-dark">AgriVision AI</h1>
                                </div>

                                <h2 className="h5 text-center text-dark mb-4">Crear Cuenta</h2>

                                <form onSubmit={handleSubmit}>
                                    {/* Nombre */}
                                    <div className="mb-3">
                                        <label htmlFor="fullName" className="form-label">Nombre Completo</label>
                                        <div className="input-group">
                                            <input
                                                type="text"
                                                className="form-control"
                                                id="fullName"
                                                placeholder="Ingresa tu nombre"
                                                name="full_name"
                                                value={formData.full_name}
                                                onChange={handleInputChange}
                                                required
                                            />
                                        </div>
                                    </div>

                                    {/* Teléfono */}
                                    <div className="mb-3">
                                        <label htmlFor="phone" className="form-label">Teléfono</label>
                                        <div className="input-group">
                                            <input
                                                type="tel"
                                                className="form-control"
                                                id="phone"
                                                placeholder="56 9 1234 5678"
                                                name="phone_number"
                                                value={formData.phone_number}
                                                onChange={handleInputChange}
                                                required
                                            />
                                        </div>
                                    </div>

                                    {/* Avatar */}

                                    <div className="form-group mb-3 ">
                                        <label htmlFor="btnAvatar" className="form-label">Imágen de Perfil:</label>
                                        <input
                                            type="file"
                                            className="form-control border-0"
                                            id="btnAvatar"
                                            placeholder="Cargar Imágen"
                                            name="avatar"
                                            onChange={(event) => {
                                                const file = event.target.files[0];
                                                setFormData(currentFormData => ({
                                                    ...currentFormData,
                                                    avatar: file,
                                                }));
                                            }}
                                        />
                                    </div>

                                    {/* Correo */}
                                    <div className="mb-3">
                                        <label htmlFor="email" className="form-label">Correo electrónico</label>
                                        <div className="input-group">
                                            <span className="input-group-text">
                                                <i className="fas fa-envelope text-secondary"></i>
                                            </span>
                                            <input
                                                type="email"
                                                className="form-control"
                                                id="email"
                                                placeholder="Ingresa tu correo"
                                                name="email"
                                                value={formData.email}
                                                onChange={handleInputChange}
                                                required
                                            />
                                        </div>
                                    </div>

                                    {/* Contraseña */}
                                    <div className="mb-3">
                                        <label htmlFor="password" className="form-label">Contraseña</label>
                                        <div className="input-group">
                                            <span className="input-group-text">
                                                <i className="fas fa-lock text-secondary"></i>
                                            </span>
                                            <input
                                                type={showPassword ? 'text' : 'password'}
                                                className="form-control"
                                                id="password"
                                                placeholder="Ingresa tu contraseña"
                                                name="password"
                                                value={formData.password}
                                                onChange={handleInputChange}
                                                required
                                            />
                                            <button
                                                type="button"
                                                className="btn btn-outline-secondary"
                                                onClick={() => setShowPassword(!showPassword)}
                                                tabIndex={-1}
                                            >
                                                <i className={`fas ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                                            </button>
                                        </div>
                                    </div>

                                    {/* Aceptación de términos */}
                                    <div className="mb-3">
                                        <div className="form-check">
                                            <input
                                                type="checkbox"
                                                className="form-check-input"
                                                id="acceptTerms"
                                                name="acceptTerms"
                                                checked={formData.acceptTerms}
                                                onChange={handleInputChange}
                                                required
                                            />
                                            <label className="form-check-label" htmlFor="acceptTerms">
                                                Acepto los términos y condiciones.
                                            </label>
                                        </div>
                                    </div>

                                    {/* Botón */}
                                    <button
                                        type="submit"
                                        className="btn btn-success w-100"
                                        disabled={isLoading}
                                    >
                                        {isLoading ? 'Creando cuenta...' : 'Crear cuenta'}
                                    </button>
                                </form>

                                <div className="text-center mt-4">
                                    <p className="small text-muted">
                                        ¿Ya tienes una cuenta?{' '}
                                        <Link to="/login" className="text-success fw-semibold text-decoration-none">
                                            Inicia sesión
                                        </Link>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
import { useState } from "react"
import useGlobalReducer from "../hooks/useGlobalReducer"
import { useSearchParams, Link, useNavigate } from "react-router-dom"


const initialStateUser = {
    email: '',
    password: '',
    showPassword: false,
}

export const Login = () => {

    const { dispatch, store } = useGlobalReducer()

    const navigate = useNavigate()

    const [searchParams, _] = useSearchParams()

    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    const [userForm, setUserForm] = useState(initialStateUser)

    const handleChange = ({ target }) => {
        setUserForm({
            ...userForm,
            [target.name]: target.value
        })
    }

    const handleSubmit = async (event) => {
        event.preventDefault();
        setIsLoading(true); // Activar loading

        try {
            const urlBackend = import.meta.env.VITE_BACKEND_URL;

            const response = await fetch(`${urlBackend}/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(userForm)
            });

            const data = await response.json();

            if (response.ok) {

                console.log("Login exitoso, token recibido:", data.token); // Debug
                localStorage.setItem("token", data.token);

                dispatch({
                    type: "login",
                    payload: data.token
                });

                setTimeout(() => {
                    setIsLoading(false),
                        navigate("/profile")
                }, 1000);

            } else if (response.status === 400) {
                alert("Credenciales incorrectas")
            } else {
                alert("Error al iniciar sesión, comunicate con soporte al cliente")
            }
        } catch (error) {
            console.error("Error en login:", error);
            alert("Error de conexión");
        } finally {
            setIsLoading(false); // Desactivar loading
        }
    };

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

                                <h2 className="h5 text-center text-dark mb-4">Iniciar sesión</h2>

                                <form onSubmit={handleSubmit}>
                                    {/* Correo */}
                                    <div className="mb-3">
                                        <label htmlFor="emailInput" className="form-label">Correo electrónico</label>
                                        <div className="input-group">
                                            <span className="input-group-text">
                                                <i className="fas fa-envelope text-secondary"></i>
                                            </span>
                                            <input
                                                type="email"
                                                className="form-control"
                                                id="emailInput"
                                                placeholder="Ingresa tu correo"
                                                name="email"
                                                value={userForm.email}
                                                onChange={handleChange}
                                                // onChange={(event) => setEmail(event.target.value)}
                                                required
                                            />
                                        </div>
                                        <div className="invalid-feedback">
                                            Este campo es obligatorio.
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
                                                value={userForm.password}
                                                onChange={handleChange}
                                                // onChange={(event) => setPassword(event.target.value)}
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
                                        <div className="invalid-feedback">
                                            Este campo es obligatorio.
                                        </div>
                                    </div>

                                    {/* Enlace */}
                                    <div className="d-flex justify-content-between align-items-center mb-3">
                                        <Link to="/recovery-password" className="text-decoration-none text-success small">
                                            ¿Olvidaste tu contraseña?
                                        </Link>
                                    </div>

                                    {/* Botón */}
                                    <button
                                        type="submit"
                                        className="btn btn-success w-100"
                                        disabled={isLoading}
                                    >
                                        {isLoading ? 'Iniciando sesión...' : 'Iniciar sesión'}
                                    </button>
                                </form>

                                <div className="text-center mt-4">
                                    <p className="small text-muted">
                                        ¿No tienes una cuenta?{' '}
                                        <Link to="/register" className="text-success fw-semibold text-decoration-none">
                                            Crear cuenta
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
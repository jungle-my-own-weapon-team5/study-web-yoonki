import { useNavigate } from "react-router-dom";

const Header = (props: any) => {

    const navigate = useNavigate();

    const onLogoClick = () => {
        navigate(`/`);
    }

    return <div className="flex justify-evenly">
        <div>
            <span className="cursor-pointer" onClick={()=>navigate(`/`)}>Main</span>
        </div>
        <div>
            <span className="cursor-pointer" onClick={()=>navigate(`/login`)}>login</span>
        </div>
        <div>
            <span className="cursor-pointer" onClick={()=>navigate(`/register`)}>register</span>
        </div>
    </div>
}

export default Header;
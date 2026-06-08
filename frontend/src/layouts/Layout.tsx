import Header from "./Header";

const Layout = (props: {
    children: React.ReactNode
}) => {
    
    return <div>
        <Header/>
        <main>
            {props.children}
        </main>
    </div>
}

export default Layout;
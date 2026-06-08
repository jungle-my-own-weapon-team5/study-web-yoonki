import Layout from "../layouts/Layout";

const BoardItem = () => {
    return <div>
        <div>
            This is mock title.
        </div>
    </div>
}

const MainPage = () => {
    return <Layout>
        <div>
            This is main page
        </div>
        <div>
            <BoardItem/>
        </div>
    </Layout>
}

export default MainPage;

import mongoose from "mongoose"
import { DB_NAME } from "../constants.js"

const connectDB=async()=>{
    try{
        const connectionInstance=await mongoose.connect(`${process.env.MONGODB_URI}/${DB_NAME}`,{family:4})
        console.log(`MongoDB connected !! DB HOST:${connectionInstance.connection.host}`)
       
    }catch(error){

        console.log("MONGODB NOT CONNECTED: ",error)
    }
}
export default connectDB;
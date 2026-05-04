import mongoose from "mongoose"
import mongooseAggregatePaginate from "mongoose-aggregate-paginate-v2"
const dailyentrySchema=new mongoose.Schema({
    user:{
        type:mongoose.Schema.Types.ObjectId,
        ref:"User"
    },
    date:{
        type: Date,
        required: true
    },
    subject:{
        type:String,
        required:true,
        trim:true
    },
    hours:{
        type:Number,
        required:true,
        min:0
    }
},{timestamps:true})
dailyentrySchema.plugin(mongooseAggregatePaginate)
export const dailyEntry=mongoose.model("dailyEntry",dailyentrySchema)
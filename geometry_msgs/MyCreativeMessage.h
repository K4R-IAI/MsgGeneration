#pragma once

#include ROSBridgeMsg.h

#include "std_msgs/String.h"
#include "string.h"

namespace geometry_msgs
{
	class MyCreativeMessage : public FROSBridgeMsg
	{
		std_msgs::String MyString
		FString MyOtherString
		uint32 SomeNumber;
	};
}
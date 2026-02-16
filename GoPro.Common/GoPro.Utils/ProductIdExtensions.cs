namespace GoPro.Utils
{
	public static class ProductIdExtensions
	{
		public static string ToStringExtended(this ProductId product)
		{
			return product switch
			{
				ProductId.REELSTEADY => "9MVQWLR1CR4G", 
				ProductId.REELSTEADY_REDEEM => "9MW025WST6RN", 
				ProductId.REELSTEADY_QA => "9PN9LPLTDQXR", 
				_ => null, 
			};
		}
	}
}

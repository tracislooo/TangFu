$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System;
using System.IO;
using System.Drawing;
using System.Drawing.Imaging;
public static class VerticalProgressVariants {
  public static void Build(string source,string output) {
    Directory.CreateDirectory(output);
    using(var src=new Bitmap(source))
    using(var preview=new Bitmap(680,270))
    using(var g=Graphics.FromImage(preview))
    using(var font=new Font("Arial",12)) {
      if(src.Width!=5 || src.Height!=20) throw new Exception("Unexpected source size");
      g.Clear(Color.FromArgb(238,240,244));
      g.DrawString("Bottom to top | Original fixed gradient | 5 x 20 px",font,Brushes.Black,14,12);
      string report="segment,percent,width,height,filled_height,first_filled_y,verified_unchanged_pixels\r\n";
      for(int n=1;n<=9;n++) {
        int height=n*2,top=20-height,verified=0;
        using(var dst=new Bitmap(5,20,PixelFormat.Format24bppRgb)) {
          using(var dg=Graphics.FromImage(dst)) dg.Clear(Color.White);
          for(int y=top;y<20;y++) for(int x=0;x<5;x++) {
            Color c=src.GetPixel(x,y);
            // Copy all original colors at their original coordinates. Only the
            // new top's first two rows receive the original rounded-cap mask.
            if(y<top+2 && y<19) {
              int cy=y-top;
              var center=src.GetPixel(2,cy);
              double denominator=255-Math.Min(center.R,Math.Min(center.G,center.B));
              double sum=0;
              foreach(int sx in new int[]{x,4-x}) {
                var edge=src.GetPixel(sx,cy);
                sum+=(255-Math.Min(edge.R,Math.Min(edge.G,edge.B)))/denominator;
              }
              double coverage=Math.Min(1,sum/2);
              c=Color.FromArgb((int)Math.Round(255-(255-c.R)*coverage),
                (int)Math.Round(255-(255-c.G)*coverage),
                (int)Math.Round(255-(255-c.B)*coverage));
            }
            dst.SetPixel(x,y,c);
          }
          string name=String.Format("progress_{0:00}_of_10_{1:00}percent.png",n,n*10);
          dst.Save(Path.Combine(output,name),ImageFormat.Png);
          using(var saved=new Bitmap(Path.Combine(output,name))) {
            if(saved.Width!=5 || saved.Height!=20) throw new Exception("Wrong canvas");
            for(int y=0;y<top;y++) for(int x=0;x<5;x++)
              if(saved.GetPixel(x,y).ToArgb()!=Color.White.ToArgb()) throw new Exception("Nonempty upper area");
            for(int y=top+2;y<20;y++) for(int x=0;x<5;x++) {
              if(saved.GetPixel(x,y).ToArgb()!=src.GetPixel(x,y).ToArgb()) throw new Exception("Gradient changed");
              verified++;
            }
            for(int x=0;x<5;x++) if(saved.GetPixel(x,19).ToArgb()!=src.GetPixel(x,19).ToArgb()) throw new Exception("Bottom moved");
            // Rounded corners are lighter than the original at the same coordinates.
            if(saved.GetPixel(0,top).ToArgb()==src.GetPixel(0,top).ToArgb()) throw new Exception("Top cap absent");
          }
          report+=String.Format("{0},{1},5,20,{2},{3},{4}\r\n",n,n*10,height,top,verified);
          int px=20+(n-1)*73;
          g.InterpolationMode=System.Drawing.Drawing2D.InterpolationMode.NearestNeighbor;
          g.PixelOffsetMode=System.Drawing.Drawing2D.PixelOffsetMode.Half;
          g.DrawImage(dst,new Rectangle(px,54,40,160),0,0,5,20,GraphicsUnit.Pixel);
          g.DrawString((n*10)+"%",font,Brushes.Black,px,226);
        }
      }
      preview.Save(Path.Combine(output,"preview.png"),ImageFormat.Png);
      File.WriteAllText(Path.Combine(output,"verification.csv"),report);
      File.WriteAllText(Path.Combine(output,"README.txt"),"9 PNG images: 1-9 of 10 (10%-90%). Canvas remains 5x20 pixels.\r\nBottom fixed at original row 19. Filled height is 2,4,...18 pixels. Original gradient colors retain their exact coordinates.\r\nTop rounded corners use coverage sampled from the original top two rows. The original bottom cap is preserved.\r\nWhite background retained from original JPEG.\r\n");
    }
  }
}
'@ -ReferencedAssemblies System.Drawing
[VerticalProgressVariants]::Build('K:\桌面\hiddenatt.jpg','G:\Doc\ChatGPT\New project\竖向进度条-1至9段')
